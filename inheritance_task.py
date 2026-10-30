class Course:
    
    name = "Fundamentals of Computer Science"
    contact_website = "www.hyperiondev.com"
    head_office = "Cape Town"

    def contact_details(self):
        print("Please contact us by visiting", self.contact_website)

    def print_head_office_location(self):
        print("Head office location:", self.head_office)


class OOPCourse(Course):
   
    def __init__(self):
        self.description = "OOP Fundamentals"
        self.trainer = "Mr Anon A. Mouse"

    def trainer_details(self):
        print("Course description:", self.description)
        print("Trainer:", self.trainer)

    def show_course_id(self):
        print("Course ID:", "#12345")


# Create an object of the subclass
course_1 = OOPCourse()

# Call the methods
course_1.contact_details()
course_1.trainer_details()
course_1.show_course_id()