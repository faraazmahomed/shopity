def largest_number(numbers):
    if len(numbers) == 1:
        return numbers[0]
    else:
        max_in_remaining = largest_number(numbers[1:])

        if numbers[0] > max_in_remaining:
            return numbers[0]
        else:
            return max_in_remaining



print(largest_number([1, 4, 5, 3]))  

print(largest_number([3, 1, 6, 8, 2, 4, 5]))  