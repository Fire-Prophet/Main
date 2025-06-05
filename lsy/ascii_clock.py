from time import strftime, sleep
import os

while True:
    os.system("cls" if os.name == "nt" else "clear")
    current_time = strftime("%H:%M:%S")
    print(f"""
     ___  ___  ___  ___
    | {current_time[:2]} || {current_time[3:5]} || {current_time[6:]} |
     ---  ---  ---  ---
    """)
    sleep(1)
