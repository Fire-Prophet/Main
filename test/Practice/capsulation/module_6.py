import math

class MathOperations:
    def square_root(self, number):
        if number < 0:
            raise ValueError("Cannot calculate square root of a negative number")
        return math.sqrt(number)

    def factorial(self, number):
        if number < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        return math.factorial(number)
