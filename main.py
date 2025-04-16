#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Snake AI Game Launcher
This script launches the Snake AI game with a trained or new model
"""

import sys
from src.agent.trainer import train
from src.menu import show_menu

if __name__ == '__main__':
    # Display menu and get user choice
    use_existing_model = show_menu()
    
    # Launch the game with the appropriate parameter
    train(use_existing_model=use_existing_model)