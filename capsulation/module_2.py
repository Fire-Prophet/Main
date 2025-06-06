import string
import random

def generate_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

class StringManipulator:
    def __init__(self, initial_string=None):
        self.string = initial_string if initial_string else generate_random_string()

    def get_string(self):
        return self.string

    def reverse_string(self):
        return self.string[::-1]
