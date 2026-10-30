import math

# Ask the user to input their desired calculation

calculation = input("Will you be calculating your investment or your bond?")

if calculation == "investment":
 
    P = float(input("Enter the amount (in rands): "))
    r = float(input("Enter the interest rate (in decimals)): "))/100
    t = int(input("Provide the number of years you will be investing (years): "))

    interest = input("Enter either 'simple' or 'compound' for the type of interest you will receive")
    Simpletotal = P*(1+r*t)
    Compoundtotal = P*math.pow((1+r),t)

# Output projections

    if interest == "simple":
        print("Your total return will be: ",Simpletotal)
    elif interest == "compound":
        print ("Your total return will be: ",Compoundtotal)

if calculation == "bond":

# Input data

    presentvalue = int(input("What is the present value of the house?"))
    intt = float(input("What is the interest rate?"))
    months = int(input("How many months will you be repaying your bond?"))

# Output monthly repayment amount

    repayment = (intt*presentvalue)/(1-(1+intt)**(-months))
    print("Your monthly repayment amount will be: ",repayment)