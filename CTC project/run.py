from flask import Flask
from app.routes import add_routes  # Import the function to register routes
from app.models import RLAgent  # Import the RLAgent class
import os

# Initialize the Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask App!"
# Initialize actions (difficulty levels)
actions = ['Easy', 'Medium', 'Hard']

# Load the RL agent (if exists)
try:
    if os.path.exists('rl_agent.pkl'):
        rl_agent = RLAgent.load_agent('rl_agent.pkl')
    else:
        rl_agent = RLAgent(actions)
except Exception as e:
    print(f"Error loading or initializing RLAgent: {e}")
    rl_agent = RLAgent(actions)  # Fallback to initializing a new RLAgent

# Register routes using the add_routes function
try:
    add_routes(app, rl_agent)
except Exception as e:
    print(f"Error registering routes: {e}")

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Error starting the Flask app: {e}")
