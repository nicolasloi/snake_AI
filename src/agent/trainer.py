"""
Training module for Snake AI Agent
"""

import matplotlib.pyplot as plt
from IPython import display
from src.game import SnakeGameAI
from src.agent.action import Agent

def plot(scores, mean_scores):
    """
    Displays a graph of scores during training
    """
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
    """
    Main training function for the agent
    
    Args:
        use_existing_model: If True, uses an existing model if available
    """
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent(use_existing_model=use_existing_model)
    game = SnakeGameAI()
    
    while True:
        # Get current state
        state_old = agent.get_state(game)
        
        # Get action to perform
        final_move, prediction_scores = agent.get_action(state_old)
        agent.last_prediction_scores = prediction_scores
        
        # Execute action and get new state
        reward, done, score = game.play_step(final_move, agent)
        state_new = agent.get_state(game)
        
        # Train short-term memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        
        # Remember data for long-term memory training
        agent.remember(state_old, final_move, reward, state_new, done)

        # If game is over
        if done:
            game.reset()
            agent.n_games += 1
            
            # Train long-term memory
            agent.train_long_memory()

            # Check if we've reached a new record
            if score > agent.record:
                agent.record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', agent.record)

            # Update data for plotting
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            
            # Display the graph
            plot(plot_scores, plot_mean_scores)