# visualization.py
# 시뮬레이션 결과 시각화
import matplotlib.pyplot as plt
import numpy as np

def visualize_simulation(sim, step):
    plt.figure(figsize=(6, 6))
    plt.imshow(sim.grid, cmap='hot', vmin=0, vmax=2)
    plt.title(f"Fire Simulation Step {step}")
    plt.axis('off')
    plt.savefig(f"fire_step_{step:03d}.png")
    plt.close()
