import math
def flight_cost(city_flight):
    if city_flight in flight_price:
        cost_flight = flight_price[city_flight]
    else:
        cost_flight = 3000
    return cost_flight


def hotel_cost(num_nights):
    cost_hotel = num_nights * 2000
    return cost_hotel


def car_rental(rental_days):
    rental_cost = rental_days * 500
    return rental_cost


def holiday_cost(num_nights, city_flight, rental_days):
    """
    This function computes the cost of 
            holiday
    """
    cost_holiday = hotel_cost(num_nights) + car_rental(rental_days) + flight_cost(city_flight)
    return cost_holiday


city_flight = input("Where are you going?").capitalize()
num_nights = int(input("How many nights are you staying?"))
rental_days = int(input("How many days do you need a car?"))
flight_price = {
    'Madrid': 3000,
    'London': 2000,
    'Geneva': 2500,
    'Rome': 3000,
        }
cost_holiday = holiday_cost(num_nights, city_flight, rental_days)

print(f"The total cost of the holiday will be {cost_holiday}")
















