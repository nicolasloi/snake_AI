"""
Model Module for Snake AI
Contains neural network components for the reinforcement learning agent
"""

from src.model.network import Linear_QNet
from src.model.trainer import QTrainer

__all__ = ["Linear_QNet", "QTrainer"]