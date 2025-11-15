import pyautogui
import random
import time


keys = ['w', 'a', 's', 'd']


try:
    while True:
        key = random.choice(keys)
        hold_time = random.uniform(1, 5)
        
        pyautogui.keyDown(key)
        time.sleep(hold_time)
        pyautogui.keyUp(key)

        pause = random.uniform(0.5, 2)
        time.sleep(pause)

except KeyboardInterrupt:
    exit()
