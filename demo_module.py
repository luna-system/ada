"""
Demo module for autonomous bug fixing demonstration.

This module contains an intentional bug that Ada should fix autonomously.
The bug: An off-by-one error in the range calculation.

Created: December 19, 2025
For: Autonomous bug fixing demo
"""


def calculate_sum(n: int) -> int:
    """Calculate the sum of numbers from 1 to n (inclusive).
    
    Args:
        n: The upper limit (inclusive)
        
    Returns:
        The sum of all numbers from 1 to n
        
    Example:
        >>> calculate_sum(5)
        15  # 1 + 2 + 3 + 4 + 5 = 15
        
        >>> calculate_sum(10)
        55  # 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10 = 55
    """
    # BUG: This should be range(1, n+1) not range(1, n)
    # Currently it calculates 1 + 2 + ... + (n-1) instead of 1 + 2 + ... + n
    total = 0
    for i in range(1, n):  # ← THE BUG IS HERE
        total += i
    return total


def calculate_product(n: int) -> int:
    """Calculate the product of numbers from 1 to n (factorial).
    
    Args:
        n: The number to calculate factorial for
        
    Returns:
        n! (n factorial)
        
    Example:
        >>> calculate_product(5)
        120  # 5! = 5 × 4 × 3 × 2 × 1 = 120
    """
    if n <= 1:
        return 1
    
    product = 1
    for i in range(1, n + 1):  # This one is correct
        product *= i
    return product


if __name__ == "__main__":
    # These will show the bug
    print(f"Sum 1 to 5: {calculate_sum(5)} (expected: 15, actual: {calculate_sum(5)})")
    print(f"Sum 1 to 10: {calculate_sum(10)} (expected: 55, actual: {calculate_sum(10)})")
    print(f"Product 1 to 5: {calculate_product(5)} (expected: 120)")
