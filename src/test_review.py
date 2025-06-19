#!/usr/bin/env python3
"""
Test file to verify Claude code review workflows.
This file intentionally violates several coding standards to test automation.
"""

# This function is too long (violates 60-line limit)
def overly_long_function_that_violates_standards():
    """This function intentionally violates coding standards for testing."""
    # Line 1
    print("Starting very long function")
    # Line 2  
    print("This function will exceed 60 lines")
    # Line 3
    print("to test our coding standards enforcement")
    # Line 4
    print("Line 4")
    # Line 5
    print("Line 5")
    # Line 6
    print("Line 6")
    # Line 7
    print("Line 7")
    # Line 8
    print("Line 8")
    # Line 9
    print("Line 9")
    # Line 10
    print("Line 10")
    # Line 11
    print("Line 11")
    # Line 12
    print("Line 12")
    # Line 13
    print("Line 13")
    # Line 14
    print("Line 14")
    # Line 15
    print("Line 15")
    # Line 16
    print("Line 16")
    # Line 17
    print("Line 17")
    # Line 18
    print("Line 18")
    # Line 19
    print("Line 19")
    # Line 20
    print("Line 20")
    # Line 21
    print("Line 21")
    # Line 22
    print("Line 22")
    # Line 23
    print("Line 23")
    # Line 24
    print("Line 24")
    # Line 25
    print("Line 25")
    # Line 26
    print("Line 26")
    # Line 27
    print("Line 27")
    # Line 28
    print("Line 28")
    # Line 29
    print("Line 29")
    # Line 30
    print("Line 30")
    # Line 31
    print("Line 31")
    # Line 32
    print("Line 32")
    # Line 33
    print("Line 33")
    # Line 34
    print("Line 34")
    # Line 35
    print("Line 35")
    # Line 36
    print("Line 36")
    # Line 37
    print("Line 37")
    # Line 38
    print("Line 38")
    # Line 39
    print("Line 39")
    # Line 40
    print("Line 40")
    # Line 41
    print(f"This is line 41 and we're still going")
    # Line 42
    print(f"This is line 42 - way past our 60 line limit")
    # Line 43
    print(f"Line 43 - definitely violating coding standards now")
    # Line 44
    print(f"Line 44")
    # Line 45
    print(f"Line 45")
    # Line 46
    print(f"Line 46")
    # Line 47
    print(f"Line 47")
    # Line 48
    print(f"Line 48")
    # Line 49
    print(f"Line 49")
    # Line 50
    print(f"Line 50")
    # Line 51
    print(f"Line 51")
    # Line 52
    print(f"Line 52")
    # Line 53
    print(f"Line 53")
    # Line 54
    print(f"Line 54")
    # Line 55
    print(f"Line 55")
    # Line 56
    print(f"Line 56")
    # Line 57
    print(f"Line 57")
    # Line 58
    print(f"Line 58")
    # Line 59
    print(f"Line 59")
    # Line 60
    print(f"Line 60 - at the limit")
    # Line 61
    print(f"Line 61 - NOW we're violating the 60-line function limit!")
    # Line 62
    print(f"Line 62 - Claude should catch this")
    # Line 63
    print(f"Line 63 - This violates docs/coding_standards.md")
    # Line 64
    return "Function completed with standards violations"

# Bad variable names (violate descriptive naming)
def bad_naming_function():
    """Function with poor variable naming to test standards checking."""
    a = 5  # Non-descriptive single letter variable
    b = 10  # Another bad variable name
    c = a + b  # Yet another bad name
    d = "test"  # Single letter for non-iterator
    
    # This should trigger warnings about non-descriptive names
    return c

# Function without error handling (should trigger suggestion)
def no_error_handling():
    """Function that should have error handling but doesn't."""
    # This opens a file without any error handling
    # Should trigger coding standards suggestion
    with open("nonexistent_file.txt") as f:
        data = f.read()
    return data

# Complex logic without comments (should trigger suggestion)
def complex_logic_no_comments():
    """Complex logic that needs comments but doesn't have them."""
    result = []
    for i in range(100):
        for j in range(50):
            if i % 2 == 0 and j % 3 == 0 or i > 75 and j < 10:
                result.append(i * j)
    return result

# Test wildfire-specific patterns
def print_fire_grid():
    """This should trigger wildfire-specific warnings about grid display."""
    # This violates our "no visual grid display" architecture rule
    print("Fire Grid Map:")
    print("🔥🔥🌲🌲")
    print("🔥🔥🌲🌲") 
    print("🌲🌲🌲🌲")
    return "grid displayed"

if __name__ == "__main__":
    overly_long_function_that_violates_standards()
    bad_naming_function()
    print_fire_grid()