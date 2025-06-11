class Agent:
    def __init__(self, agent_id, initial_state):
        self.agent_id = agent_id
        self.state = initial_state
        self.history = []

    def update_state(self, new_state):
        self.history.append(self.state)
        self.state = new_state

    def get_state(self):
        return self.state

    def __repr__(self):
        return f"Agent({self.agent_id}, {self.state})"

# Example usage:
# agent1 = Agent(agent_id="agent_001", initial_state={"position": (0,0), "mood": "neutral"})
# agent1.update_state({"position": (1,0), "mood": "curious"})
# print(agent1.get_state())
# print(agent1.history)