from django.apps import apps

# Use get_model to dynamically import models
def get_model(model_name):
    return apps.get_model('main_app', model_name)

def get_default_role():
    Role = get_model('Role')    
    return Role.objects.first()

def get_default_season():
    Season = get_model('Season')
    return Season.objects.first()

def get_default_car():
    Car = get_model('Car')
    # Assuming there's a way to identify the default Car instance, e.g., by name
    default_car = Car.objects.filter(name='Default Car').first()
    if default_car:
        return default_car  # Return the default Car instance
    else:
        # Handle the case where the default Car instance does not exist
        # This could involve creating a default Car instance and returning it
        # For demonstration purposes, let's assume we return None
        return None

