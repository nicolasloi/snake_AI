"""
Memory management module for Snake AI Agent
"""

from collections import deque

# Maximum memory size
MAX_MEMORY = 100_000
# Batch size for learning
BATCH_SIZE = 1000

class ReplayMemory:
    """
    Replay memory for storing agent experiences
    """
    def __init__(self, max_size=MAX_MEMORY):
        self.memory = deque(maxlen=max_size)
    
    def remember(self, state, action, reward, next_state, done):
        """
        Stores an experience in memory
        """
        self.memory.append((state, action, reward, next_state, done))
    
    def get_batch(self, batch_size=BATCH_SIZE):
        """
        Retrieves a batch of experiences for learning
        
        Returns:
            Mini-batch of random experiences from memory
        """
        import random
        if len(self.memory) > batch_size:
            mini_sample = random.sample(self.memory, batch_size)
        else:
            mini_sample = list(self.memory)
            
        return mini_sample