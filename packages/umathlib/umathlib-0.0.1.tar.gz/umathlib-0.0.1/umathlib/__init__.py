def add(*numbers):
    """
    takes numbers (separated by comma) and perform addition
    """
    sum = 0
    for number in numbers:
        sum += number
    return sum
        
def subtract(number1, number2):
    """
    takes (number1, number2) and subtract number2 from number1
    """
    return number1 - number2

def multiply(*numbers):
    """
    takes numbers (separated by comma) and perform multiplication
    """
    result = 0
    for number in numbers:
        result *= number
    return result
        
def divide(number1, number2):
    """
    takes (number1, number2) and divide number1 by number2
    """
    return number1 / number2