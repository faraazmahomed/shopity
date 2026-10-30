class Shoe:
    """Represents a single shoe item in the inventory.

    Attributes:
        country (str): The country where the shoe was manufactured.
        code (str): The unique product code of the shoe.
        product (str): The model or name of the shoe.
        cost (float): The unit cost price of the shoe.
        quantity (int): The total stock volume available.
    """

    def __init__(self, country, code, product, cost, quantity):
        """Initializes a new instance of the Shoe class.

        Args:
            country (str): Country of origin.
            code (str): Unique product code identifier.
            product (str): Product model name.
            cost (float): Unit price.
            quantity (int): Current stock count.
        """
        self.country = country
        self.code = code
        self.product = product
        self.cost = cost
        self.quantity = quantity

    def get_cost(self):
        """Retrieves the cost price of the shoe instance.

        Returns:
            float: The cost price of the shoe.
        """
        return self.cost

    def get_quantity(self):
        """Retrieves the remaining stock quantity of the shoe.

        Returns:
            int: The current quantity available in stock.
        """
        return self.quantity

    def __str__(self):
        """Generates a human-readable string layout of the shoe data.

        Returns:
            str: Formatted text summarizing all attributes.
        """
        return (
            f"Country: {self.country} | Code: {self.code} | "
            f"Product: {self.product} | Cost: ${self.cost:.2f} | "
            f"Quantity: {self.quantity}"
        )


# ============= Shoe list ===========
shoe_list = []


# ========== Functions outside the class ==============

def save_shoes_data():
    """Overwrites 'inventory.txt' with the current state of shoe_list.

    This function loops through all Shoe objects currently stored in the
    global shoe_list variable and writes them back to the disk file in
    the original comma-separated value format, preserving headers.

    Returns:
        None
    """
    try:
        with open("inventory.txt", "w") as file:
            # Write required file header format
            file.write("Country,Code,Product,Cost,Quantity\n")
            for shoe in shoe_list:
                line = (
                    f"{shoe.country},{shoe.code},{shoe.product},"
                    f"{shoe.cost},{shoe.quantity}\n"
                )
                file.write(line)
        print("Data successfully synchronized to 'inventory.txt'.")
    except Exception as error:
        print(f"Error saving data to file: {error}")


def read_shoes_data():
    """Reads inventory lines from 'inventory.txt' and builds shoe_list.

    Parses data row-by-row, strips whitespace, converts numeric data types,
    instantiates unique Shoe objects, and saves them to the list. Skips the
    initial row containing table headers.

    Returns:
        None
    """
    try:
        with open("inventory.txt", "r") as file:
            next(file)  # Skip the header line
            for line in file:
                clean_line = line.strip()
                if clean_line:
                    shoe_split = clean_line.split(',')
                    if len(shoe_split) >= 5:
                        country = shoe_split[0].strip()
                        code = shoe_split[1].strip()
                        product = shoe_split[2].strip()
                        cost = float(shoe_split[3].strip())
                        quantity = int(shoe_split[4].strip())

                        new_shoe = Shoe(
                            country, code, product, cost, quantity
                        )
                        shoe_list.append(new_shoe)
        print("Inventory data loaded successfully.")
    except FileNotFoundError:
        print(" 'inventory.txt' not found. Empty inventory started.")
    except Exception as error:
        print(f"Error reading file: {error}")


def capture_shoes():
    """Prompts user for entries to create and append a new shoe.

    Includes explicit string length checking logic ensuring that the user
    enters real characters for the country, code, and product fields. It
    validates numeric constraints, saves the shoe to shoe_list, and triggers
    save_shoes_data() to permanently record the changes.

    Returns:
        None
    """
    print("\n--- Capture New Shoe Data ---")

    country = input("Enter country: ").strip()
    code = input("Enter shoe code: ").strip()
    product = input("Enter product name: ").strip()

    # Explicit check to ensure all input strings contain actual information
    if not country or not code or not product:
        print("Error: String inputs cannot be left blank.")
        return

    try:
        cost = float(input("Enter cost: "))
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Error: Cost must be numeric. Quantity must be int.")
        return

    new_shoe = Shoe(country, code, product, cost, quantity)
    shoe_list.append(new_shoe)
    print(f"Success: {product} has been added to memory.")

    # Rewrite database text file with changes appended
    save_shoes_data()


def view_all():
    """Iterates through shoe_list and prints every shoe object.

    Uses the __str__ special method formatting built directly into the
    Shoe blueprint to display clean inventory rows. Handles empty arrays
    gracefully.

    Returns:
        None
    """
    if not shoe_list:
        print("Inventory is currently empty.")
        return
    print("\n--- Current Shoe Inventory ---")
    for shoe in shoe_list:
        print(shoe)


def re_stock():
    """Identifies the lowest stocked shoe item and prompts for increments.

    Locates the matching stock minimum via an implicit min comparison. If
    confirmed by user entry input, the existing object's capacity variable
    is directly modified and immediately rewritten to 'inventory.txt'.

    Returns:
        None
    """
    if not shoe_list:
        print("Inventory is empty.")
        return

    lowest_shoe = min(shoe_list, key=lambda shoe: shoe.quantity)

    print(
        f"\nThe lowest stock item is: {lowest_shoe.product} "
        f"(Quantity: {lowest_shoe.quantity})"
    )

    msg = "Would you like to re-stock this item? (yes/no): "
    answer = input(msg).strip().lower()

    if answer == "yes":
        try:
            msg_units = "How many units would you like to add? "
            add_stock = int(input(msg_units))
            shoe_index = shoe_list.index(lowest_shoe)
            lowest_shoe.quantity += add_stock
            shoe_list[shoe_index] = lowest_shoe

            print(
                f"Successfully restocked! New quantity is "
                f"{shoe_list[shoe_index].quantity}")

            # Rewrite database text file with updated quantities
            save_shoes_data()

        except ValueError:
            print("Invalid entry. Must be an integer.")

    elif answer == "no":
        print(f"You will run out of {lowest_shoe.product}")


def search_shoe():
    """Queries shoe_list to discover an entry matching a search code string.

    Args:
        None (Uses input terminal interaction prompt dynamically).

    Returns:
        Shoe: The object matching the product identifier string code,
              or None if no structural match is found.
    """
    msg = "\nEnter the shoe code you are searching for: "
    search_code = input(msg).strip().lower()

    for shoe in shoe_list:
        if str(shoe.code).lower() == search_code:
            print(f"\nMatch found:\n{shoe}")
            return shoe

    print("Shoe code not found.")
    return None


def value():
    """Prints total calculated financial asset worth per item line.

    Performs math processing calculations using: Value = Cost * Quantity.
    Iterates dynamically across all shoe records loaded in state.

    Returns:
        None
    """
    print("\n--- Total Financial Value of Stock ---")
    for shoe in shoe_list:
        try:
            cost = float(shoe.cost)
            quantity = int(shoe.quantity)
            total_val = cost * quantity
            print(
                f"Product: {shoe.product} | "
                f"Stock Value: ${total_val:.2f}"
            )
        except ValueError:
            print(
                f"Error calculating value for {shoe.product}: "
                f"Invalid cost or quantity data type."
            )


def highest_qty():
    """Identifies item with the largest volume and prints it for sale.

    Locates the supreme upper metric boundary using an int evaluation
    sorting lambda mapping function inside max().

    Returns:
        None
    """
    if not shoe_list:
        print("Inventory empty.")
        return

    highest_shoe = max(shoe_list, key=lambda shoe: int(shoe.quantity))
    print(
        f"\n🔥 SALE item: {highest_shoe.product} has the "
        f"highest stock ({highest_shoe.quantity} units) "
        f"and is for sale!"
    )


# ========== Main Menu =============

def main_menu():
    """Controls administrative choice menus and system lifecycles.

    Runs an infinite while loop checking operational options from 1 to 8,
    matching terminal keyboard numbers against inventory action logic blocks.

    Returns:
        None
    """
    read_shoes_data()

    while True:
        print("\n======== Shoe Management System ========")
        print("1. Read shoes data from file")
        print("2. Capture a new shoe")
        print("3. View all shoes")
        print("4. Re-stock lowest quantity item")
        print("5. Search for a shoe by code")
        print("6. View total financial value per item")
        print("7. View highest quantity (Sale) item")
        print("8. Exit")

        choice = input("Enter your choice (1-8): ").strip()

        if choice == '1':
            shoe_list.clear()
            read_shoes_data()
        elif choice == '2':
            capture_shoes()
        elif choice == '3':
            view_all()
        elif choice == '4':
            re_stock()
        elif choice == '5':
            search_shoe()
        elif choice == '6':
            value()
        elif choice == '7':
            highest_qty()
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Enter a number from 1 to 8.")


if __name__ == "__main__":
    main_menu()
