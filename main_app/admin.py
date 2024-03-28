from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# from main_app import booking_views
from .models import *
from main_app.models import Season

# Register your models here.


class UserModel(UserAdmin):
    ordering = ('email',)


admin.site.register(CustomUser, UserModel)
admin.site.register(Staff)
admin.site.register(booking)
admin.site.register(Role)
admin.site.register(Car)
admin.site.register(Season)
