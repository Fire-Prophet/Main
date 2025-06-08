import random

class MathProblem:
    def __init__(self):
        self.num1 = random.randint(1, 20)
        self.num2 = random.randint(1, 20)
        self.operator = random.choice(['+', '-', '*'])
        self.answer = self.calculate_answer()

    def calculate_answer(self):
        if self.operator == '+':
            return self.num1 + self.num2
        elif self.operator == '-':
            return self.num1 - self.num2
        elif self.operator == '*':
            return self.num1 * self.num2

    def display(self):
        return f"{self.num1} {self.operator} {self.num2} = ?"

    def check_answer(self, user_input):
        try:
            return int(user_input) == self.answer
        except ValueError:
            return False
