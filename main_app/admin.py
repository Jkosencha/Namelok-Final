from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from main_app.models import Season

# Register your models here.


class UserModel(UserAdmin):
    ordering = ('email',)


admin.site.register(CustomUser, UserModel)
admin.site.register(Staff)
admin.site.register(Inquiry)
admin.site.register(Booking)
admin.site.register(Role)
admin.site.register(Car)
admin.site.register(Season)
