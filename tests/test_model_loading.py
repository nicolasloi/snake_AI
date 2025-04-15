import torch
import os
import sys
import os.path as path

# Ajouter le répertoire parent au path pour pouvoir importer depuis src
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from src.model import Linear_QNet
from src.agent import Agent

def test_model_loading():
    """
    Test if the model loading mechanism works correctly.
    This function creates an Agent which should automatically load the saved model,
    and displays model information to verify loading succeeded.
    """
    print("===== Testing Model Loading =====")
    
    # Check if model file exists
    model_path = os.path.join('./model', 'model.pth')
    if os.path.exists(model_path):
        print(f"Model file found at {model_path}")
        
        # Create two instances of the model
        print("\nCreating a new model with default weights...")
        new_model = Linear_QNet(11, 256, 3)
        
        print("\nCreating an agent that should load the saved model...")
        agent = Agent()
        loaded_model = agent.model
        
        # Compare parameters to verify loading
        print("\nVerifying model loading:")
        
        # Check if parameters are different (they should be if loading worked)
        params_different = False
        for (name1, param1), (name2, param2) in zip(new_model.named_parameters(), loaded_model.named_parameters()):
            if not torch.allclose(param1, param2):
                params_different = True
                print(f"- Parameter '{name1}' is different between models ✓")
                
        if params_different:
            print("\n✅ SUCCESS: Model loading works correctly! The loaded model has different weights than a new model.")
        else:
            print("\n❌ FAILURE: Model loading might not be working. The loaded model has the same weights as a new model.")
    else:
        print(f"❌ No saved model found at {model_path}. Please train the model first.")

if __name__ == "__main__":
    test_model_loading()