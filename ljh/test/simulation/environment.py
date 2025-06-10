class ForestEnvironment:
    def __init__(self, name, size_hectares):
        self.name = name
        self.size_hectares = size_hectares
        self.description = "A vast forest environment on a mountain."
        self.terrain_type = "mountainous"
        self.vegetation = ["pine trees", "oak trees", "undergrowth", "ferns"]
        self.weather_conditions = {"temperature_celsius": 15, "precipitation_mm": 0, "wind_kph": 5}
        self.agents_present = [] # To store agents within this environment
        self.resources = {"water_sources": 5, "food_patches": 10}

    def get_description(self):
        return f"{self.name}: A {self.terrain_type} forest spanning {self.size_hectares} hectares."

    def add_agent(self, agent):
        if agent not in self.agents_present:
            self.agents_present.append(agent)
            # Optionally, update agent's state to reflect being in this environment
            # agent.update_state({"current_environment": self.name})

    def remove_agent(self, agent):
        if agent in self.agents_present:
            self.agents_present.remove(agent)

    def update_weather(self, new_weather_conditions):
        self.weather_conditions.update(new_weather_conditions)
        print(f"Weather in {self.name} updated: {self.weather_conditions}")

    def __repr__(self):
        return f"ForestEnvironment({self.name}, {self.size_hectares}ha)"

# Example usage:
# mountain_forest = ForestEnvironment(name="Misty Mountain Forest", size_hectares=10000)
# print(mountain_forest.get_description())
# mountain_forest.update_weather({"temperature_celsius": 12, "precipitation_mm": 5})

# To integrate with Agent class from agent_model.py (assuming it's in the same directory or accessible):
# from agent_model import Agent 
# agent1 = Agent(agent_id="deer_001", initial_state={"type": "herbivore", "location": "forest_edge"})
# mountain_forest.add_agent(agent1)
# print(mountain_forest.agents_present)