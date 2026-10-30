# Prompt the user to enter their age and convert the input to an integer.
age = int(input("Enter age : "))

# Check if the age is less than 18 and print appropriate message.
if age < 18:
    print("You are a minor")

# Check if the age is less than 10 and print appropriate message.
elif age < 10:
    print("You are a minor who is less than 10 years")

# Check if the age is less than 5 and print appropriate message.
elif age < 5:
    print("You are minor who is less than 5 years")

# Check if the age is less than 3 and print appropriate message.
elif age < 3:
    print("You are just a toddler")

# If none of the above conditions are met, print a message indicating the person is a major.
else:
    print("You are a major !")