from pynput.keyboard import ConTroller
import time

text = "hiiiiiiii "

time.sleep(8)
keyboard = Controller()

for char in text:
    keyboard.type(char)
    time.sleep(0.6)
    