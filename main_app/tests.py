from django.apps import apps
from django.test import TestCase

# from main_app.forms import Season, Car

# Create your tests here.
def get_default_season():
        Season = apps.get_model('main_app', 'Season')
    # Replace this with the logic to get the default Season instance
    # For example, you might return the first Season instance in the database
        return Season.objects.first().id

def get_default_car():
    Car = apps.get_model('main_app', 'Car')
    Staff = apps.get_model('main_app', 'Staff')
    # Assuming you have a Car model and you want to use the first instance as the default
    # This assumes there is at least one Car instance in the database
    car = Car.objects.first()
    # Check if a Car object was found
    if car is not None:
        # Return the id of the first Car object
        return car.id
    else:
        # Handle the case where no Car objects exist
        # For example, you might want to create a default Car object
        # or return a default value
        # Here's an example of creating a default Car object
        staff = Staff.objects.first()
        if staff is None:
            # If no Staff objects exist, create a default Staff object
            staff = Staff.objects.create(name='Default Staff')
        default_car = Car.objects.create(name='Default Car', staff=staff)
        return default_car.id