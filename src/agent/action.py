"""
Action management module for Snake AI Agent
"""

import torch
import random
import numpy as np
import os
from src.agent.memory import ReplayMemory
from src.agent.state import get_state
from src.model.network import Linear_QNet

class Agent:
    """
    Reinforcement learning agent for Snake game
    """
    def __init__(self, use_existing_model=True):
        self.n_games = 0
        self.record = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = ReplayMemory()
        
        # Enhanced state with 5-block vision instead of 3:
        # 15 dangers (3 directions x 5 blocks), 4 current directions, 4 relative food positions
        self.model = Linear_QNet(23, 256, 3)
        
        # For visualization
        self.prev_food_distance = 0
        self.approaching_food = False
        self.last_prediction_scores = None
        
        # Load existing model if available
        model_folder_path = './model'
        file_name = os.path.join(model_folder_path, 'model.pth')
        self.trained_model_loaded = False
        
        if os.path.exists(file_name) and use_existing_model:
            try:
                # Load model with size difference handling
                saved_state = torch.load(file_name)
                
                # Check if the old model had a different size
                if 'linear1.weight' in saved_state and saved_state['linear1.weight'].size(1) != 23:
                    print(f"The existing model is not compatible with the new 5-block vision. Creating a new model.")
                else:
                    self.model.load_state_dict(saved_state)
                    self.model.eval()  # Set model to evaluation mode
                    self.trained_model_loaded = True
                    print(f"Model loaded from {file_name}")
                    
                    # Reduce exploration with a trained model
                    self.n_games = 60
                    print(f"Starting with reduced exploration (equivalent to {self.n_games} games experience)")
                
            except Exception as e:
                print(f"Error loading model: {e}. Starting with a new model.")
        else:
            if not use_existing_model:
                print("Starting with a new model as requested.")
            else:
                print("No saved model found. Starting with a new model.")
            
        from src.model.trainer import QTrainer
        self.trainer = QTrainer(self.model, lr=0.001, gamma=self.gamma)

    def get_state(self, game):
        """
        Gets the current state of the game
        """
        return get_state(game)

    def remember(self, state, action, reward, next_state, done):
        """
        Stores an experience in memory
        """
        self.memory.remember(state, action, reward, next_state, done)

    def train_long_memory(self):
        """
        Trains the model on a batch of experiences
        """
        mini_sample = self.memory.get_batch()
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        """
        Trains the model on a single experience
        """
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        """
        Determines the action to take based on the current state
        
        Returns:
            final_move: action vector [straight, right_turn, left_turn]
            prediction_scores: prediction scores for visualization
        """
        # Determine exploration rate
        if self.trained_model_loaded:
            self.epsilon = max(20 - self.n_games, 0)  # Lower exploration rate
        else:
            self.epsilon = 80 - self.n_games  # Original exploration rate
            
        final_move = [0, 0, 0]
        prediction_scores = None
        
        if random.randint(0, 200) < self.epsilon:
            # Random move (exploration)
            move = random.randint(0, 2)
            final_move[move] = 1
            # Create fake prediction scores for visualization
            prediction_scores = [0.0, 0.0, 0.0]
            prediction_scores[move] = 1.0
        else:
            # Model-predicted move (exploitation)
            state_tensor = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state_tensor)
            # Apply softmax to get probabilities
            prediction_probs = torch.nn.functional.softmax(prediction, dim=0)
            prediction_scores = prediction_probs.detach().numpy()
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move, prediction_scores