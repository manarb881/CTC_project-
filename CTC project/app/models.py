import numpy as np
import pickle


class RLAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.99):
        """
        Initialize the RL Agent.

        :param actions: List of possible actions (difficulty levels: Easy, Medium, Hard).
        :param alpha: Learning rate for Q-learning.
        :param gamma: Discount factor for future rewards.
        :param epsilon: Initial exploration rate.
        :param epsilon_decay: Decay rate for exploration over time.
        """
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.q_table = {}  # State-action table

    def adjust_exploration_rate(self, avg_score):
        """
        Dynamically adjust the exploration rate based on the user's average score.

        :param avg_score: Average score of the user in the current session.
        """
        try:
            if avg_score == 10:  # Favor exploitation if performance is high
                self.epsilon *= self.epsilon_decay
            else:  # Favor exploration if performance is low
                self.epsilon = min(1.0, self.epsilon / self.epsilon_decay)
        except Exception as e:
            print(f"Error adjusting exploration rate: {e}")

    def choose_action(self, state):
        """
        Choose an action based on the current state using an epsilon-greedy strategy.

        :param state: Current state (e.g., skill level).
        :return: Chosen action (difficulty level).
        """
        try:
            if np.random.rand() < self.epsilon:
                # Explore: Choose a random action
                return np.random.choice(self.actions)
            else:
                # Exploit: Choose the action with the highest Q-value for the current state
                return self._get_best_action(state)
        except Exception as e:
            print(f"Error choosing action: {e}")
            return np.random.choice(self.actions)

    def _get_best_action(self, state):
        """
        Get the action with the highest Q-value for a given state.

        :param state: Current state (e.g., skill level).
        :return: Best action (difficulty level).
        """
        try:
            if state not in self.q_table:
                return np.random.choice(self.actions)
            return max(self.q_table[state], key=self.q_table[state].get)
        except Exception as e:
            print(f"Error getting best action: {e}")
            return np.random.choice(self.actions)

    def update_q_table(self, state, action, reward, next_state):
        """
        Update the Q-value for a given state-action pair.

        :param state: Current state.
        :param action: Action taken.
        :param reward: Reward received.
        :param next_state: Next state after taking the action.
        """
        try:
            if state not in self.q_table:
                self.q_table[state] = {a: 0.0 for a in self.actions}

            if next_state not in self.q_table:
                self.q_table[next_state] = {a: 0.0 for a in self.actions}

            current_q = self.q_table[state][action]
            max_next_q = max(self.q_table[next_state].values())
            self.q_table[state][action] = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        except Exception as e:
            print(f"Error updating Q-table: {e}")

    def save_agent(self, filepath):
        """
        Save the agent's state to a file.

        :param filepath: Path to save the agent's state.
        """
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self, f)
        except Exception as e:
            print(f"Error saving agent: {e}")

    @staticmethod
    def load_agent(filepath):
        """
        Load the agent's state from a file.

        :param filepath: Path to load the agent's state from.
        :return: Loaded RLAgent object.
        """
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading agent: {e}")
            return None
