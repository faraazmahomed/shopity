def adding_up_to(list_of_integers, index):
   
    if index <= 0:
        return list_of_integers[0]

    return list_of_integers[index] + adding_up_to(list_of_integers, index - 1)

result = adding_up_to([1, 4, 5, 3, 12, 16], 4)
print(result) 

result = adding_up_to([4, 3, 1, 5], 1)
print(result)  