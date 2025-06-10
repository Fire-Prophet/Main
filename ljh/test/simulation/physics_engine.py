import random

class PhysicsEngine:
    def __init__(self, environment):
        self.environment = environment
        self.fire_events = [] # Stores active fire events: {"location": (x,y), "intensity": 0-100, "spread_radius": meters}

    def simulate_fire_spread(self, fire_event):
        """
        Simulates the spread of a single fire event.
        More complex logic can be added based on wind, terrain, fuel, etc.
        """
        # Increase intensity based on some logic (e.g., fuel availability - simplified here)
        if fire_event["intensity"] < 100:
            fire_event["intensity"] += random.randint(1, 5) # Random increase
            fire_event["intensity"] = min(fire_event["intensity"], 100)

        # Increase spread radius
        # Spread rate could depend on intensity, wind, fuel type from environment.vegetation
        spread_increase = fire_event["intensity"] / 20  # Example: higher intensity, faster spread
        fire_event["spread_radius"] += spread_increase

        # Potentially affect environment (e.g., consume vegetation, change weather)
        # This would require more detailed environment interaction
        # For now, we just print a message
        print(f"Fire at {fire_event['location']} spreading. Intensity: {fire_event['intensity']}, Radius: {fire_event['spread_radius']:.2f}m")

        # Check if fire should extinguish (e.g., ran out of fuel, or rain)
        if self.environment.weather_conditions.get("precipitation_mm", 0) > 2: # If it's raining significantly
            fire_event["intensity"] -= random.randint(5, 15) # Rain reduces intensity
            fire_event["intensity"] = max(fire_event["intensity"], 0)
            if fire_event["intensity"] == 0:
                print(f"Fire at {fire_event['location']} extinguished by rain.")
                return True # Mark for removal
        return False # Fire continues

    def add_fire_event(self, location, initial_intensity=10, initial_spread_radius=1):
        """Adds a new fire event to the simulation."""
        new_fire = {"location": location, "intensity": initial_intensity, "spread_radius": initial_spread_radius}
        self.fire_events.append(new_fire)
        print(f"New fire started at {location} with intensity {initial_intensity} and radius {initial_spread_radius}m.")

    def update_physics(self):
        """Updates all physical simulations, including fire events."""
        fires_to_remove = []
        for fire in self.fire_events:
            if self.simulate_fire_spread(fire):
                fires_to_remove.append(fire)
        
        for fire in fires_to_remove:
            self.fire_events.remove(fire)

        # Other physics simulations can be added here (e.g., agent movement, resource changes)

    def get_active_fires(self):
        return self.fire_events

# Example Usage (requires Environment class from environment.py)
# from environment import ForestEnvironment
# mountain_forest = ForestEnvironment(name="Misty Mountain Forest", size_hectares=10000)
# physics_sim = PhysicsEngine(environment=mountain_forest)

# Start a fire
# physics_sim.add_fire_event(location=(150, 200), initial_intensity=20)

# In a simulation loop, you would call:
# physics_sim.update_physics()
# print(physics_sim.get_active_fires())

# Simulate rain to see if it extinguishes the fire
# mountain_forest.update_weather({"precipitation_mm": 5})
# physics_sim.update_physics() # Fire intensity should decrease
# print(physics_sim.get_active_fires())
