import random

chars = ["*", "#", "@", "%", "&", "+", "=", "-", "~"]
width = 40
height = 20

for _ in range(height):
    print("".join(random.choice(chars) for _ in range(width)))
