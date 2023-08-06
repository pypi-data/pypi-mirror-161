# Importing NumPy as "np"
import numpy as np

class add:

    def __init__(self, num1, num2):
        self.num1 = num1
        self.num2 = num2


    def multiply(self):
        
        # Using NumPy .dot() to multiply the numbers
        return np.sum(self.num1, self.num2)