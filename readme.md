# Snake AI Project

A reinforcement learning project that teaches an AI to play the classic Snake game using Deep Q-Learning.

## Overview

This project implements a Snake game with an AI agent that learns to play through reinforcement learning. The AI uses a neural network to determine optimal moves based on the current game state.

## Project Structure

- **src/game.py**: The Snake game environment built with Pygame
- **src/agent.py**: The reinforcement learning agent that plays and learns the game
- **src/model.py**: Neural network architecture and training logic
- **tests/**: Contains test scripts to validate functionality
- **main.py**: Main entry point to run the game
- **model/**: Directory where trained models are saved

## Installation

1. Clone the repository
2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## How It Works

The system uses Deep Q-Learning with the following components:

### State Representation

The AI receives information about:

- Danger in three directions (straight, right, left)
- Current movement direction
- Food location relative to the snake's head

### Action Space

The agent can choose to:

- Move straight [1,0,0]
- Turn right [0,1,0]
- Turn left [0,0,1]

### Reward System

- +10 points for eating food
- -10 points for collisions or timing out
- The agent aims to maximize cumulative rewards

### Learning Process

- Uses an epsilon-greedy strategy (balancing exploration vs. exploitation)
- Stores experiences in a memory buffer for training
- Updates neural network weights through backpropagation

## Running the Project

To start training:

```bash
python main.py
```

To run the model loading test (verifies that a trained model loads correctly):

```bash
python tests/test_model_loading.py
```

The game window displays:

- Current game score
- Number of games played
- High score record
- Visual representation of the snake, food, and environment

## Requirements

- Python 3.x
- PyTorch
- Pygame
- Matplotlib (for displaying training progress)
- NumPy

## Training Progress

The neural network model is automatically saved to `model/model.pth` whenever the agent achieves a new high score, allowing training to be resumed later. When you start the game, it automatically loads the previously trained model if one exists, so you don't need to start from scratch each time.

The model loading test script (`tests/test_model_loading.py`) can be used to verify that the model loading functionality is working correctly.

## Credits

This implementation is based on reinforcement learning concepts and the Deep Q-Learning algorithm.
