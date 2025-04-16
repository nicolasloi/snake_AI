"""
Neural network module for Snake AI
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    """
    Simple neural network for reinforcement learning Q-learning
    """
    def __init__(self, input_size, hidden_size, output_size):
        """
        Initializes the network with input, hidden, and output layers
        
        Args:
            input_size: size of input layer
            hidden_size: size of hidden layer
            output_size: size of output layer
        """
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        """
        Forward propagation through the neural network
        
        Args:
            x: input tensor
            
        Returns:
            network output
        """
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        """
        Saves the model to a file
        
        Args:
            file_name: name of file to save the model
        """
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)