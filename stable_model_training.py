"""
Minimum working example to train a Lunar Lander Agent using a DQN algorithm

Apollo Ammonites - NMA Deep Learning 2021
Team members:
    J. A. Moreno-Larios
    ADD YOURSELVES HERE
    Giordano Ramos-Traslosheros

Requirements:
    xvfb - X-display for headless systems
    python-opengl - for movie rendering
    ffmpeg - for movie rendering
    stable-baseline3 - RNN framework
    box2d-py
    gym - Scenes
    pyvirtualdisplay
    matplotlib
    numpy
    - Note that there will be additional dependencies. pip, anaconda or 
        miniconda should be able to install them.
    - For miniconda, be sure to execure 
    'conda config --add channels conda-forge' to be able to 
    install software on an isolated environment
    - To have CUDA support, you'll need to run 
        conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch
        https://pytorch.org/get-started/locally/

"""

# Imports
import io
import os
import glob
import torch
import base64
import stable_baselines3

from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
from stable_baselines3.common.results_plotter import load_results, ts2xy, plot_results
import matplotlib.pyplot as plt

import gym
from gym.wrappers import Monitor

# Plotting/Video functions
from IPython.display import HTML
from pyvirtualdisplay import Display
from IPython import display as ipythondisplay

#display = Display(visible=0, size=(1400, 900))
#display.start()

"""
Utility functions to enable video recording of gym environment
and displaying it.
To enable video, just do "env = wrap_env(env)""
"""

def show_video():
    mp4list = glob.glob('video/*.mp4')
    if len(mp4list) > 0:
        mp4 = mp4list[0]
        video = io.open(mp4, 'r+b').read()
        encoded = base64.b64encode(video)
        ipythondisplay.display(HTML(data='''<video alt="test" autoplay
            loop controls style="height: 400px;">
            <source src="data:video/mp4;base64,{0}" type="video/mp4" />
            </video>'''.format(encoded.decode('ascii'))))
    else:
        print("Could not find video")

def wrap_env(env, subdir):
    env = Monitor(env, './video/' + subdir, force = True)
    return env

"""
Basic DQN implementation
"""

nn_layers = [256, 256] #This is the configuration of your neural network. Currently, we have two layers, each consisting of 64 neurons.
                    #If you want three layers with 64 neurons each, set the value to [64,64,64] and so on.

learning_rate = 0.001 #This is the step-size with which the gradient descent is carried out.
                        #Tip: Use smaller step-sizes for larger networks.
reward_threshold = 300 # Stop condition

log_dir = "./tmp/gym/stable/"
os.makedirs(log_dir, exist_ok=True)


env = gym.make('LunarLander-v2')

#You can also load other environments like cartpole, MountainCar, Acrobot. Refer to https://gym.openai.com/docs/ for descriptions.
#For example, if you would like to load Cartpole, just replace the above statement with "env = gym.make('CartPole-v1')".
env = stable_baselines3.common.monitor.Monitor(env, log_dir )
# Configure the env so it stops when threshold is reached
callback_on_best = StopTrainingOnRewardThreshold(reward_threshold=reward_threshold, verbose=1)
callback = EvalCallback(env,log_path = log_dir, callback_on_new_best=callback_on_best, deterministic=True) #For evaluating the performance of the agent periodically and logging the results.
policy_kwargs = dict(activation_fn=torch.nn.ReLU,
                             net_arch=nn_layers)
model = DQN("MlpPolicy", env,policy_kwargs = policy_kwargs,
                    learning_rate=learning_rate,
                    batch_size=32,  #for simplicity, we are not doing batch update.
                    buffer_size=50000, #size of experience of replay buffer. Set to 1 as batch update is not done
                    learning_starts=25000, #learning starts immediately!
                    gamma=0.99, #discount facto. range is between 0 and 1.
                    tau = 1,  #the soft update coefficient for updating the target network
                    target_update_interval=1000, #update the target network after # steps
                    train_freq=(1,"step"), #train the network at every step.
                    max_grad_norm = 100, #the maximum value for the gradient clipping
                    exploration_initial_eps = 1, #initial value of random action probability
                    exploration_fraction = 0.05, #fraction of entire training period over which the exploration rate is reduced
                    exploration_final_eps = 0.1,
                    gradient_steps = -1, #number of gradient steps
                    seed = 1, #seed for the pseudo random generators
                    verbose = 0) #Set verbose to 1 to observe training logs. We encourage you to set the verbose to 1.

"""
Here we train the model
"""

model.learn(total_timesteps=1000000, log_interval=100, callback=callback)
# The performance of the training will be printed every 100 episodes. 
#Change it to 1, if you wish to view the performance at 
# every training episode.

# We save the model here
model.save('test_model_edits_2.zip')

# We plot the rewards
fig, axs = plt.subplots(2)
fig.suptitle("Reward plots")
x_timesteps, y_rewards = ts2xy(load_results(log_dir), 'timesteps')
axs[0].plot(x_timesteps, y_rewards)
axs[0].ylim([-500, 500])
axs[0].xlabel("Time steps [1]")
axs[0].ylabel("Reward [points]")
axs[0].title("Rewards per time step [units]")

x_episodes, y_episode_rewards = ts2xy(load_results(log_dir), 'episodes')
axs[1].ylim([-500, 500])
axs[1].plot(x_episodes, y_episode_rewards)
axs[1].ylim([-500, 500])
axs[1].xlabel("Episodes [1]")
axs[1].ylabel("Reward [points]")
axs[1].title("Rewards per episode [units]")

"""
Now we render the lander behavior and display it on video
"""

test_env = wrap_env(gym.make("LunarLander-v2"), "after_training_edits_stable")
observation = test_env.reset()
total_reward = 0
while True:
  test_env.render()
  action, _states = model.predict(observation, deterministic=True)
  observation, reward, done, info = test_env.step(action)
  total_reward += reward
  if done:
    break;
print(total_reward)
test_env.close()
#show_video()

