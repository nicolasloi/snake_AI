"""
Training module for Snake AI model
"""

import torch
import torch.nn as nn
import torch.optim as optim

class QTrainer:
    """
    Trainer for the Q-learning network
    """
    def __init__(self, model, lr, gamma):
        """
        Initializes the trainer with necessary parameters
        
        Args:
            model: neural network model to train
            lr: learning rate
            gamma: discount factor for future rewards
        """
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        """
        Performs one training step of the model
        
        Args:
            state: current state
            action: action taken
            reward: reward received
            next_state: next state
            done: boolean indicating if the episode is finished
        """
        # Convert data to tensors if not already
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        # Handle dimensions for single-item batches
        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        # Q prediction for current state
        pred = self.model(state)

        # Q prediction for next state (Q_new = r + gamma * max(Q_next))
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
                
            # Update Q value for the action taken
            target[idx][torch.argmax(action[idx]).item()] = Q_new

        # Update network weights
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()