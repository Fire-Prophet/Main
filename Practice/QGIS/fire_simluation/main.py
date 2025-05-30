# main.py
# 산불 화재 시뮬레이션 메인 실행 파일
from fire_model import FireSimulation
from environment import Environment
from visualization import visualize_simulation

def main():
    env = Environment(dem_path="../dem.tif", wind_speed=5, wind_dir=90, humidity=30)
    sim = FireSimulation(env, ignition_points=[(50, 50)])
    for step in range(100):
        sim.step()
        visualize_simulation(sim, step)
        if sim.is_extinguished():
            print(f"불이 {step} 스텝 만에 진화되었습니다.")
            break

if __name__ == "__main__":
    main()
