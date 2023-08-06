import numpy as np


class AverageRewardTracker():
    current_index = 0

    def __init__(self, num_rewards_for_average=100):
        self.num_rewards_for_average = num_rewards_for_average
        self.last_x_rewards = []
        self.sum = 0
        self.number = 0

    def add(self, reward):
        if len(self.last_x_rewards) < self.num_rewards_for_average:
            self.last_x_rewards.append(reward)
            self.sum += reward
            self.number += 1
        else:
            self.sum += reward - self.last_x_rewards[self.current_index]
            self.last_x_rewards[self.current_index] = reward
            self.__increment_current_index()

    def __increment_current_index(self):
        self.current_index += 1
        if self.current_index >= self.num_rewards_for_average:
            self.current_index = 0

    def get_average(self):
        if self.number == 0:
            return 0
        return self.sum / self.number
