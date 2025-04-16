"""
Snake AI Project
A reinforcement learning project that trains an AI to play the Snake game
"""

from src.game import SnakeGameAI, Direction, Point
from src.agent import Agent, train
from src.model import Linear_QNet, QTrainer
from src.menu import show_menu

__all__ = [
    "SnakeGameAI", "Direction", "Point",
    "Agent", "train",
    "Linear_QNet", "QTrainer",
    "show_menu"
]