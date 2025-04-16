import torch
import random
import numpy as np
import os
from collections import deque
from src.game import SnakeGameAI, Direction, Point
from src.model import Linear_QNet, QTrainer
import matplotlib.pyplot as plt
from IPython import display
import time

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001  # learning rate


class Agent:
    def __init__(self, use_existing_model=True):
        self.n_games = 0
        self.record = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(17, 256, 3)  # Updated: 17 inputs (9 dangers + 4 directions + 4 food positions)
        
        # Track distances to food for better visualization
        self.prev_food_distance = 0
        self.approaching_food = False
        
        # Check if a trained model exists and load it
        model_folder_path = './model'
        file_name = os.path.join(model_folder_path, 'model.pth')
        self.trained_model_loaded = False
        
        if os.path.exists(file_name) and use_existing_model:
            try:
                self.model.load_state_dict(torch.load(file_name))
                self.model.eval()  # Set the model to evaluation mode
                self.trained_model_loaded = True
                print(f"Loaded trained model from {file_name}")
                
                # Start with more experience (less exploration) when a model is loaded
                self.n_games = 60  # This reduces epsilon to a lower value
                print(f"Starting with reduced exploration (equivalent to {self.n_games} games of experience)")
                
            except Exception as e:
                print(f"Error loading model: {e}. Starting with a new model.")
        else:
            if not use_existing_model:
                print("Starting with a new model as requested.")
            else:
                print("No saved model found. Starting with a new model.")
            
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        
    def get_best_action(self, state, thinking_time):
        """
        Exécute plusieurs inférences pendant le temps imparti et 
        retourne l'action qui a la meilleure probabilité moyenne.
        
        Args:
            state: état actuel du jeu
            thinking_time: temps maximum en secondes pour réfléchir
            
        Returns:
            (final_move, prediction_scores, inference_count): 
                - l'action choisie
                - les scores de prédiction moyens
                - le nombre d'inférences effectuées
        """
        # Si le temps de réflexion est très court, faire une seule inférence
        if thinking_time <= 0.001:
            return self.get_action(state)

        # Si en phase d'exploration, faire une action aléatoire
        # Utiliser la même logique que dans get_action
        if self.trained_model_loaded:
            epsilon = max(20 - self.n_games, 0)
        else:
            epsilon = 80 - self.n_games
            
        if random.randint(0, 200) < epsilon:
            move_idx = random.randint(0, 2)
            final_move = [0, 0, 0]
            final_move[move_idx] = 1
            fake_scores = [0.0, 0.0, 0.0]
            fake_scores[move_idx] = 1.0
            return final_move, fake_scores, 1
        
        # Convertir l'état en tensor pour le modèle
        state_tensor = torch.tensor(state, dtype=torch.float)
        
        # Accumulateurs pour les prédictions
        action_scores = [0, 0, 0]
        inference_count = 0
        
        # Temps de début
        start_time = time.time()
        
        # Continuer jusqu'à ce que le temps soit écoulé
        while time.time() - start_time < thinking_time:
            # Obtenir une prédiction du modèle
            with torch.no_grad():  # Pas besoin de calculer des gradients
                prediction = self.model(state_tensor)
                
            # Appliquer softmax pour obtenir des probabilités
            probs = torch.nn.functional.softmax(prediction, dim=0).numpy()
            
            # Ajouter à nos accumulateurs
            for i in range(3):
                action_scores[i] += probs[i]
                
            inference_count += 1
            
        # Calculer les scores moyens
        for i in range(3):
            action_scores[i] /= inference_count
            
        # Trouver l'action avec le meilleur score moyen
        move_idx = np.argmax(action_scores)
        final_move = [0, 0, 0]
        final_move[move_idx] = 1
        
        return final_move, action_scores, inference_count

    def get_state(self, game):
        head = game.snake[0]
        
        # Define points at 1, 2, and 3 blocks distance in each direction
        # Left direction
        point_l1 = Point(head.x - 20, head.y)
        point_l2 = Point(head.x - 40, head.y)
        point_l3 = Point(head.x - 60, head.y)
        
        # Right direction
        point_r1 = Point(head.x + 20, head.y)
        point_r2 = Point(head.x + 40, head.y)
        point_r3 = Point(head.x + 60, head.y)
        
        # Up direction
        point_u1 = Point(head.x, head.y - 20)
        point_u2 = Point(head.x, head.y - 40)
        point_u3 = Point(head.x, head.y - 60)
        
        # Down direction
        point_d1 = Point(head.x, head.y + 20)
        point_d2 = Point(head.x, head.y + 40)
        point_d3 = Point(head.x, head.y + 60)

        # Current direction
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        # Extended state with perception at 3 blocks
        state = [
            # Danger straight ahead - 1st block
            (dir_r and game.is_collision(point_r1)) or 
            (dir_l and game.is_collision(point_l1)) or
            (dir_u and game.is_collision(point_u1)) or
            (dir_d and game.is_collision(point_d1)),
            
            # Danger straight ahead - 2nd block
            (dir_r and game.is_collision(point_r2)) or 
            (dir_l and game.is_collision(point_l2)) or
            (dir_u and game.is_collision(point_u2)) or
            (dir_d and game.is_collision(point_d2)),
            
            # Danger straight ahead - 3rd block
            (dir_r and game.is_collision(point_r3)) or 
            (dir_l and game.is_collision(point_l3)) or
            (dir_u and game.is_collision(point_u3)) or
            (dir_d and game.is_collision(point_d3)),

            # Danger to the right - 1st block
            (dir_u and game.is_collision(point_r1)) or 
            (dir_d and game.is_collision(point_l1)) or
            (dir_l and game.is_collision(point_u1)) or
            (dir_r and game.is_collision(point_d1)),
            
            # Danger to the right - 2nd block
            (dir_u and game.is_collision(point_r2)) or 
            (dir_d and game.is_collision(point_l2)) or
            (dir_l and game.is_collision(point_u2)) or
            (dir_r and game.is_collision(point_d2)),
            
            # Danger to the right - 3rd block
            (dir_u and game.is_collision(point_r3)) or 
            (dir_d and game.is_collision(point_l3)) or
            (dir_l and game.is_collision(point_u3)) or
            (dir_r and game.is_collision(point_d3)),

            # Danger to the left - 1st block
            (dir_d and game.is_collision(point_r1)) or 
            (dir_u and game.is_collision(point_l1)) or
            (dir_r and game.is_collision(point_u1)) or
            (dir_l and game.is_collision(point_d1)),
            
            # Danger to the left - 2nd block
            (dir_d and game.is_collision(point_r2)) or 
            (dir_u and game.is_collision(point_l2)) or
            (dir_r and game.is_collision(point_u2)) or
            (dir_l and game.is_collision(point_d2)),
            
            # Danger to the left - 3rd block
            (dir_d and game.is_collision(point_r3)) or 
            (dir_u and game.is_collision(point_l3)) or
            (dir_r and game.is_collision(point_u3)) or
            (dir_l and game.is_collision(point_d3)),

            # Current direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food position relative to the head
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # If trained model is loaded, we can use a lower epsilon for less exploration
        if self.trained_model_loaded:
            self.epsilon = max(20 - self.n_games, 0)  # Lower exploration rate, minimum 0
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
            # Predicted move based on model (exploitation)
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            # Apply softmax to get probabilities
            prediction_probs = torch.nn.functional.softmax(prediction, dim=0)
            prediction_scores = prediction_probs.detach().numpy()
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move, prediction_scores


def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores) - 1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores) - 1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)


def train(use_existing_model=True):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent(use_existing_model=use_existing_model)
    game = SnakeGameAI()
    
    while True:
        state_old = agent.get_state(game)
        final_move, prediction_scores = agent.get_action(state_old)
        agent.last_prediction_scores = prediction_scores
        
        reward, done, score = game.play_step(final_move, agent)
        state_new = agent.get_state(game)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > agent.record: # Check for new record only when game is done
                agent.record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', agent.record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games # n_games is now guaranteed to be >= 1
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()
