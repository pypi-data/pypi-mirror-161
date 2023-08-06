import os

import wandb
from torch.utils.tensorboard import SummaryWriter
import time
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import gym
from maslourl.trackers.average_tracker import AverageRewardTracker
from abc import ABC, abstractmethod


class MaslouTorchModel(nn.Module, ABC):
    @abstractmethod
    def get_value(self, x):
        pass

    @abstractmethod
    def get_action_and_value(self, x, action=None):
        pass

    @abstractmethod
    def get_action_greedy(self, x):
        pass

class MaslouPPOAgentEval(ABC):
    def __init__(self, use_cuda=True, env=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() and use_cuda else "cpu")
        self.env = env
        self.agent = self.build_agent().to(self.device)

    @abstractmethod
    def build_agent(self) -> MaslouTorchModel:
        pass

    def load_agent(self, path):
        self.agent = torch.load(path)
        self.agent.eval()


class MaslouPPOAgent(ABC):

    def __init__(self, args, discrete=True):
        self.args = args
        self.discrete=discrete
        self.run_name = f"{args.gym_id}_{args.exp_name}_{args.seed}_{int(time.time())}"
        if args.track:
            import wandb

            wandb.init(project=args.wandb_project_name,
                       entity=args.wandb_entity,
                       sync_tensorboard=True,
                       config=vars(args),
                       name=self.run_name,
                       monitor_gym=True,
                       save_code=True)

        self.writer = SummaryWriter(f"runs/{self.run_name}")
        self.writer.add_text("hyperparameters",
                             "|param|value|\n|-|-|\n%s" % (
                                 "\n".join([f"|{key}|{value}" for key, value in vars(args).items()])))
        random.seed(args.seed)
        np.random.seed(args.seed)
        torch.manual_seed(args.seed)
        torch.backends.cudnn.deterministic = args.torch_deterministic
        self.device = torch.device("cuda" if torch.cuda.is_available() and args.cuda else "cpu")
        self.envs = gym.vector.SyncVectorEnv(
            [self.make_env(args.gym_id, args.seed + i, i, args.capture_video, args.capture_every_n_video, self.run_name)
             for i in
             range(args.num_envs)])
        if isinstance(self.envs.single_action_space, gym.spaces.Discrete) != self.discrete:
            raise f"Illegal type of action. You want {'discrete' if self.discrete else 'continuous'}, but gym want {self.envs.single_action_space}"
        self.agent = self.build_agent().to(self.device)

    @abstractmethod
    def make_env(self, gym_id, seed, idx, capture_video, capture_every_n_episode, run_name):
        pass

    @abstractmethod
    def build_agent(self) -> MaslouTorchModel:
        pass

    def save_agent(self):
        if not os.path.exists("./models/"):
            os.makedirs("./models/")
        torch.save(self.agent, "models/best_model.pt")
        if self.args.track and self.args.save_best_to_wandb:
            if self.args.verbose:
                print("Saving file to w&b", os.path.join(wandb.run.dir, "models/best_model.pt"))
            if not os.path.exists(os.path.join(wandb.run.dir, "models/")):
                os.makedirs(os.path.join(wandb.run.dir, "models/"))
            torch.save(self.agent, os.path.join(wandb.run.dir, "models/best_model.pt"))

    def load_agent(self, path, train=False):
        self.agent = torch.load(path)
        if train:
            self.agent.train()
        else:
            self.agent.eval()

    def train(self):
        average_reward_tracker = AverageRewardTracker(self.args.average_reward_2_save)
        best_rewards = -np.inf
        optimizer = optim.Adam(self.agent.parameters(), lr=self.args.learning_rate, eps=1e-5)
        obs = torch.zeros((self.args.num_steps, self.args.num_envs) + self.envs.single_observation_space.shape).to(
            self.device)
        actions = torch.zeros((self.args.num_steps, self.args.num_envs) + self.envs.single_action_space.shape).to(
            self.device)
        logprobs = torch.zeros((self.args.num_steps, self.args.num_envs)).to(self.device)
        rewards = torch.zeros((self.args.num_steps, self.args.num_envs)).to(self.device)
        dones = torch.zeros((self.args.num_steps, self.args.num_envs)).to(self.device)
        values = torch.zeros((self.args.num_steps, self.args.num_envs)).to(self.device)

        global_step = 0
        start_time = time.time()
        next_obs = torch.Tensor(self.envs.reset()).to(self.device)
        next_done = torch.zeros(self.args.num_envs).to(self.device)
        num_updates = self.args.total_timesteps // self.args.batch_size

        for update in range(1, num_updates + 1):
            if self.args.anneal_lr:
                frac = 1.0 - (update - 1) / num_updates
                lrnow = frac * self.args.learning_rate
                optimizer.param_groups[0]["lr"] = lrnow
            for step in range(0, self.args.num_steps):
                global_step += 1 * self.args.num_envs
                obs[step] = next_obs
                dones[step] = next_done

                with torch.no_grad():
                    action, logprob, entropy, value = self.agent.get_action_and_value(next_obs)
                    values[step] = value.flatten()
                    actions[step] = action
                    logprobs[step] = logprob
                next_obs, reward, done, info = self.envs.step(action.cpu().numpy())
                rewards[step] = torch.tensor(reward).to(self.device).view(-1)
                next_obs, next_done = torch.Tensor(next_obs).to(self.device), torch.Tensor(done).to(self.device)
                for item in info:
                    if "episode" in item.keys():
                        if self.args.verbose:
                            print(f"global_step={global_step}, episodic_return={item['episode']['r']}")
                        self.writer.add_scalar("charts/episodic_return", item["episode"]["r"], global_step)
                        self.writer.add_scalar("charts/episodic_length", item["episode"]["l"], global_step)
                        average_reward_tracker.add(item["episode"]["r"])
                        avg = average_reward_tracker.get_average()
                        if avg > best_rewards:
                            best_rewards = avg
                            self.save_agent()
                        break
            with torch.no_grad():
                next_value = self.agent.get_value(next_obs).reshape(1, -1)
                if self.args.gae:
                    advantages = torch.zeros_like(rewards).to(self.device)
                    lastgaelam = 0
                    for t in reversed(range(self.args.num_steps)):
                        if t == self.args.num_steps - 1:
                            nextnonterminal = 1.0 - next_done
                            nextvalues = next_value
                        else:
                            nextnonterminal = 1.0 - dones[t + 1]
                            nextvalues = values[t + 1]
                        delta = rewards[t] + self.args.gamma * nextvalues * nextnonterminal - values[t]
                        advantages[
                            t] = lastgaelam = delta + self.args.gamma * self.args.gae_lambda * nextnonterminal * lastgaelam
                    returns = advantages + values
                else:
                    returns = torch.zeros_like(rewards).to(self.device)
                    for t in reversed(range(self.args.num_steps)):
                        if t == self.args.num_steps - 1:
                            nextnonterminal = 1.0 - next_done
                            next_return = next_value
                        else:
                            nextnonterminal = 1.0 - dones[t + 1]
                            next_return = returns[t + 1]
                        returns[t] = rewards[t] + self.args.gamma * nextnonterminal * next_return
                    advantages = returns - values

            # flatten the batch
            b_obs = obs.reshape((-1,) + self.envs.single_observation_space.shape)
            b_logprobs = logprobs.reshape(-1)
            b_actions = actions.reshape((-1,) + self.envs.single_action_space.shape)
            b_advantages = advantages.reshape(-1)
            b_returns = returns.reshape(-1)
            b_values = values.reshape(-1)

            b_inds = np.arange(self.args.batch_size)
            for epoch in range(self.args.update_epochs):
                np.random.shuffle(b_inds)
                for start in range(0, self.args.batch_size, self.args.minibatch_size):
                    end = start + self.args.minibatch_size
                    mb_inds = b_inds[start: end]
                    _, newlogprob, entropy, newvalue = self.agent.get_action_and_value(b_obs[mb_inds],
                                                                                           b_actions.long()[mb_inds] if self.discrete else b_actions[mb_inds])


                    log_ratio = newlogprob - b_logprobs[mb_inds]
                    ratio = log_ratio.exp()

                    mb_advantages = b_advantages[mb_inds]
                    if self.args.norm_adv:
                        mb_advantages = (mb_advantages - mb_advantages.mean()) / (mb_advantages.std() + 1e-8)

                    pg_loss1 = - mb_advantages * ratio
                    pg_loss2 = -mb_advantages * torch.clip(ratio, 1 - self.args.clip_coef, 1 + self.args.clip_coef)
                    pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                    newvalue = newvalue.view(-1)
                    if self.args.clip_vloss:
                        v_loss_unclipped = (newvalue - b_returns[mb_inds]) ** 2
                        v_clipped = b_values[mb_inds] + torch.clamp(newvalue - b_returns[mb_inds],
                                                                    -self.args.clip_coef,
                                                                    self.args.clip_coef)
                        v_loss_clipped = (v_clipped - b_returns[mb_inds]) ** 2
                        v_loss_max = torch.max(v_loss_unclipped, v_loss_clipped)
                        v_loss = 0.5 * v_loss_max.mean()
                    else:
                        v_loss = 0.5 * ((newvalue - b_returns[mb_inds]) ** 2).mean()
                    entropy_loss = entropy.mean()
                    loss = pg_loss - self.args.ent_coef * entropy_loss + v_loss * self.args.vf_coef

                    optimizer.zero_grad()
                    loss.backward()
                    nn.utils.clip_grad_norm_(self.agent.parameters(), self.args.max_grad_norm)
                    optimizer.step()

            y_pred, y_true = b_values.cpu().numpy(), b_returns.cpu().numpy()
            var_y = np.var(y_true)
            explained_var = np.nan if var_y == 0 else 1 - np.var(y_true - y_pred) / var_y

            self.writer.add_scalar("charts/learning_rate", optimizer.param_groups[0]["lr"], global_step)
            self.writer.add_scalar("losses/value_loss", v_loss.item(), global_step)
            self.writer.add_scalar("losses/policy_loss", pg_loss.item(), global_step)
            self.writer.add_scalar("losses/entropy_loss", entropy_loss.item(), global_step)
            self.writer.add_scalar("losses/explained_variance", explained_var, global_step)
            self.writer.add_scalar("charts/SPS", int(global_step / (time.time() - start_time)), global_step)

        self.envs.close()
        self.writer.close()

