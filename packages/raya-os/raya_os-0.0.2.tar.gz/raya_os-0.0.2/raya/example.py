def example():
    print("Hello World!")
    return 0

#define a class with a method that takes a list of numbers as an argument and returns the sum of all numbers in the list
class Sum:
    def __init__(self, nums):
        self.nums = nums
    def sum(self):
        return sum(self.nums)
