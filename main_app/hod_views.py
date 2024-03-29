import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from .models import Role, Trips, Staff, booking, CustomUser 
from django.db import transaction
from .forms import BookingForm, roleForm, ItineraryForm

from .forms import *
from .models import *


# def admin_home(request):
#     total_staff = Staff.objects.all().count()
#     total_bookings = booking.objects.all().count()
#     all_Cars = Car.objects.all()
#     total_Car = all_Cars.count()
#     total_role = Role.objects.all().count()
#     trips_list = Trips.objects.filter(car__in=all_Cars)
#     total_trips = trips_list.count()
#     # trips_list = []
#     Car_list = []
#     for car_instance in all_Cars:
#         role = role.objects.get(id=car_instance.role.id)
#         booking_count = booking.objects.filter(role_id=role.id).count()
#         Car_list.append(car_instance.name)
#         booking_count_list_in_Car.append(booking_count)

def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_bookings = booking.objects.all().count()
    all_Cars = Car.objects.all()
    total_Car = all_Cars.count()
    total_role = Role.objects.all().count()
    trips_list = Trips.objects.filter(car__in=all_Cars)
    total_trips = trips_list.count()

    Car_list = []
    booking_count_list_in_Car = []  # Initialize the list to store booking counts
    
    for car_instance in all_Cars:
         role = Role.objects.get(id=car_instance.role.id)
         booking_count = booking.objects.filter(role_id=role.id).count()
         Car_list.append(car_instance.name)
         booking_count_list_in_Car.append(booking_count)


    # Total Cars and bookings for each staff
    all_roles = Role.objects.all()
    role_name_list = []
    Car_count_list = []
    booking_count_list_in_role = []

    for role in all_roles:
        Cars = Car.objects.filter(role_id=role.id).count()
        bookings = booking.objects.filter(role_id=role.id).count()
        role_name_list.append(role.name)
        Car_count_list.append(Cars)
        booking_count_list_in_role.append(bookings)
    
    all_Cars = Car.objects.all()
    Car_list = []
    booking_count_list_in_Car = []
    for car_instance in all_Cars:
        role = Role.objects.get(id=car_instance.role.id)
        booking_count = booking.objects.filter(role_id=role.id).count()
        Car_list.append(car_instance.name)
        booking_count_list_in_Car.append(booking_count)



    # For bookings
    booking_trips_present_list = []
    booking_trips_leave_list = []
    booking_name_list = []

    bookings = booking.objects.all()
    for booking_instance in bookings:
        
        trips = tripsReport.objects.filter(booking_id=booking_instance.id, status=True).count()
        absent = tripsReport.objects.filter(booking_id=booking_instance.id, status=False).count()
        leave = LeaveReportbooking.objects.filter(booking_id=booking_instance.id, status=1).count()
        booking_trips_present_list.append(trips)
        booking_trips_leave_list.append(leave + absent)
        booking_name_list.append(booking_instance.admin.first_name)

    context = {
        'page_title': "Administrative Dashboard",
        'total_bookings': total_bookings,
        'total_staff': total_staff,
        'total_role': total_role,
        'total_Car': total_Car,
        'Car_list': Car_list,
        'trips_list': trips_list,
        'booking_trips_present_list': booking_trips_present_list,
        'booking_trips_leave_list': booking_trips_leave_list,
        "booking_name_list": booking_name_list,
        "booking_count_list_in_Car": booking_count_list_in_Car,
        "booking_count_list_in_role": booking_count_list_in_role,
        "role_name_list": role_name_list,
    }
    return render(request, 'hod_template/home_content.html', context)





def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Staff'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            role = form.cleaned_data.get('role')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                # Create CustomUser instance
                user = CustomUser.objects.create_user(
                    email=email, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                
                # Save the user instance
                user.save()

                # Create Staff instance
                staff = Staff.objects.create(name=f"{user.last_name} {user.first_name}", role=role, admin=user)
                
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Please fulfill all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)

def add_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract form data
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            role = form.cleaned_data.get('role')
            season = form.cleaned_data.get('Season')
            profile_pic = request.FILES.get('profile_pic')

            try:
                # Create CustomUser instance
                user = CustomUser.objects.create_user(
                    email=email,
                    user_type=3,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    profile_pic=profile_pic
                )
                print(f"User created: {user.id}") # Debugging line

                # Create Booking instance and associate with user
                booking_instance = booking.objects.create(
                    user=user, # Associate the booking with the created user
                    role=role,
                    season=season
                )
                print(f"Booking created: {booking_instance.id}") # Debugging line

                messages.success(request, "Booking added successfully")
                return redirect('add_booking')
            except Exception as e:
                messages.error(request, f"Could not add booking: {e}")
    else:
        form = BookingForm()

    context = {'form': form, 'page_title': 'Add booking'}
    return render(request, 'hod_template/add_booking_template.html', context)

    #     else:
    #     messages.error(request, "Form is not valid")
    #     else:
    #     booking_form = BookingForm()

    # context = {'form': booking_form, 'page_title': 'Add booking'}
    # return render(request, 'hod_template/add_booking_template.html', context)



def add_role(request):
    form = roleForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add role'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                role = Role()  # Assuming Role is your model class for roles
                role.name = name
                role.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_role'))
            except Exception as e:
                messages.error(request, f"Could Not Add: {str(e)}")
                print(f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Form is invalid. Could Not Add")
    return render(request, 'hod_template/add_role_template.html', context)


from .models import Car  # Import the Car model at the top of your views.py file

def add_Car(request):
    form = CarForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Car'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            role = form.cleaned_data.get('role')
            staff = form.cleaned_data.get('staff')
            try:
                car_instance = Car()  # Renamed variable to avoid conflict with model class name
                car_instance.name = name
                car_instance.staff = staff
                car_instance.role = role
                car_instance.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_Car'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_Car_template.html', context)





def add_itinerary(request):
    form = ItineraryForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Itinerary'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            
            try:
                itinerary_instance = Itinerary()  # Renamed variable to avoid conflict with model class name
                itinerary_instance.name = name
                itinerary_instance.description = description
                itinerary_instance.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_itinerary'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_itinerary_template.html', context)



def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2) # Assuming CustomUser is your user model and user_type=2 represents staff
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Staff'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_booking(request):
    bookings = CustomUser.objects.filter(user_type=3)
    context = {
        'bookings': bookings,
        'page_title': 'Manage bookings'
    }
    return render(request, "hod_template/manage_booking.html", context)


def manage_role(request):
    roles = Role.objects.all()
    context = {
        'roles': roles,
        'page_title': 'Manage roles'
    }
    return render(request, "hod_template/manage_role.html", context)


def manage_Car(request):
    Cars = Car.objects.all()
    context = {
        'Cars': Cars,
        'page_title': 'Manage Cars'
    }
    return render(request, "hod_template/manage_Car.html", context)

def manage_itinerary(request):
    itinerary = Itinerary.objects.all()
    context = {
        'itinerary': itinerary,
        'page_title': 'Manage itinerary'
    }
    return render(request, "hod_template/manage_itinerary_template.html", context)



def edit_staff(request, staff_id):
    staff = get_object_or_404(staff, id=staff_id)
    user = staff.user  # Access the associated user directly through the staff object
    form = StaffForm(request.POST or None, request.FILES or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Staff'
    }
    if request.method == 'POST':
        if form.is_valid():
            # Extract form data
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            role = form.cleaned_data.get('role')
            passport = request.FILES.get('profile_pic')  # No need for "or None" here

            try:
                # Update user fields
                user.username = username
                user.email = email
                if passport:  # Check if passport is provided
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                user.save()

                # Update staff role
                staff.role = role
                staff.save()

                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, f"Could Not Update: {str(e)}")
        else:
            messages.error(request, "Please fill the form properly")
    
    # If the request method is GET or the form is invalid, render the form page
    return render(request, "hod_template/edit_staff_template.html", context)



def edit_booking(request, booking_id):
    booking = get_object_or_404(booking, id=booking_id)
    form = BookingForm(request.POST or None, instance=booking)
    context = {
        'form': form,
        'booking_id': booking_id,
        'page_title': 'Edit booking'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            # address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            role = form.cleaned_data.get('role')
            Season = form.cleaned_data.get('Season')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=booking.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                booking.Season = Season
                user.gender = gender
                # user.address = address
                booking.role = role
                user.save()
                booking.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_booking', args=[booking_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_booking_template.html", context)

def edit_role(request, role_id):
    instance = get_object_or_404(Role, id=role_id)
    form = roleForm(request.POST or None, instance=instance)  # Use RoleForm instead of roleForm
    context = {
        'form': form,
        'role_id': role_id,
        'page_title': 'Edit role'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                role_instance = instance
                role_instance.name = name
                role_instance.save()
                messages.success(request, "Successfully Updated")
            except Exception as e:
                messages.error(request, f"Could Not Update: {str(e)}")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_role_template.html', context)

def edit_Car(request, Car_id):
    instance = get_object_or_404(Car, id=Car_id)
    form = CarForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'Car_id': Car_id,
        'page_title': 'Edit Car'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            role = form.cleaned_data.get('role')
            staff = form.cleaned_data.get('staff')
            try:
                Car = Car.objects.get(id=Car_id)
                Car.name = name
                Car.staff = staff
                Car.role = role
                Car.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_Car', args=[Car_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_Car_template.html', context)



# def edit_itinerary(request, itinerary_id):
#     instance = get_object_or_404(Itinerary, id=itinerary_id)
#     form = ItineraryForm(request.POST or None, instance=instance)
#     context = {
#         'form': form,
#         'itinerary_id': itinerary_id,
#         'page_title': 'Edit itinerary'
#     }
#     if request.method == 'POST':
#         if form.is_valid():
#             name = form.cleaned_data.get('name')
#             description = form.cleaned_data.get('description')
#             try:
#                 itinerary = itinerary.objects.get(id=itinerary_id)
#                 itinerary.name = name
#                 itinerary.description = description
#                 itinerary.save()
#                 messages.success(request, "Successfully Updated")
#                 return redirect(reverse('edit_itinerary', args=[itinerary_id]))
#             except Exception as e:
#                 messages.error(request, "Could Not Add " + str(e))
#         else:
#             messages.error(request, "Fill Form Properly")
#     return render(request, 'hod_template/edit_itinerary.html', context)

def edit_itinerary(request, itinerary_id):
    instance = get_object_or_404(Itinerary, id=itinerary_id)
    
    if request.method == 'POST':
        form = ItineraryForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully Updated")
            return redirect('edit_itinerary', itinerary_id=itinerary_id)
        else:
            messages.error(request, "Fill Form Properly")
    else:
        form = ItineraryForm(instance=instance)
    context = {
        'form': form,
        'itinerary_id': itinerary_id,
        'page_title': 'Edit itinerary'
    }
    return render(request, 'hod_template/edit_itinerary.html', context)

def add_Season(request):
    form = SeasonForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Season'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Season Created")
                return redirect(reverse('add_Season'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_Season_template.html", context)


def manage_Season(request):
    seasons = Season.objects.all()  
    context = {'seasons': seasons, 'page_title': 'Manage Season'}  
    return render(request, "hod_template/manage_Season.html", context)

def edit_Season(request, Season_id):
    instance = get_object_or_404(Season, id=Season_id)
    form = SeasonForm(request.POST or None, instance=instance)
    context = {'form': form, 'Season_id': Season_id,
               'page_title': 'Edit Season'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Season Updated")
                return redirect(reverse('edit_Season', args=[Season_id]))
            except Exception as e:
                messages.error(
                    request, "Season Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_Season_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_Season_template.html", context)

    else:
        return render(request, "hod_template/edit_Season_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def booking_feedback_message(request):
    if request.method != 'POST':
        feedbacks = Feedbackbooking.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'booking Feedback Messages'
        }
        return render(request, 'hod_template/booking_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(Feedbackbooking, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Staff'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def get_admin_trips(request):
    Car_id = request.POST.get('Car')
    Season_id = request.POST.get('Season')
    trips_date_id = request.POST.get('trips_date_id')
    try:
        Car = get_object_or_404(Car, id=Car_id)
        Season = get_object_or_404(Season, id=Season_id)
        trips = get_object_or_404(
            trips, id=trips_date_id, Season=Season)
        trips_reports = tripsReport.objects.filter(
            trips=trips)
        json_data = []
        for report in trips_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.booking)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Staff",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "booking Management System",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))
    
# def delete_staff(request, staff_id):
#     staff_instance = get_object_or_404(Staff, id=staff_id)
#     try:
#         staff_instance.delete()
#         messages.success(request, "Staff deleted successfully!")
#     except Exception:
#         messages.error(
#             request, "Sorry, some bookings are assigned to this user already. Kindly change the affected booking role and try again")
#     return redirect(reverse('manage_staff'))


def delete_booking(request, booking_id):
    booking = get_object_or_404(booking, id=booking_id)
    booking.delete()
    messages.success(request, "booking deleted successfully!")
    return redirect(reverse('manage_booking'))


from django.shortcuts import get_object_or_404
from .models import Role

def delete_role(request, role_id):
    role_instance = get_object_or_404(Role, id=role_id)
    try:
        role_instance.delete()
        messages.success(request, "Role deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some bookings are assigned to this user already. Kindly change the affected booking role and try again")
    return redirect(reverse('manage_role'))


def delete_Car(request, Car_id):
    Car = get_object_or_404(Car, id=Car_id)
    Car.delete()
    messages.success(request, "Car deleted successfully!")
    return redirect(reverse('manage_Car'))

# def delete_itinerary(request, itinerary_id):
#     itinerary = get_object_or_404(Itinerary, id=itinerary_id)
#     Itinerary.delete()
#     messages.success(request, "itinerary deleted successfully!")
#     return redirect(reverse('manage_itinerary'))

def delete_itinerary(request, itinerary_id):
    itinerary = get_object_or_404(Itinerary, id=itinerary_id)
    itinerary.delete()
    messages.success(request, "Itinerary deleted successfully!")
    return redirect(reverse('manage_itinerary'))

def delete_Season(request, Season_id):
    Season = get_object_or_404(Season, id=Season_id)
    try:
        Season.delete()
        messages.success(request, "Season deleted successfully!")
    except Exception:
        messages.error(
            request, "There are bookings assigned to this Season. Please move them to another Season.")
    return redirect(reverse('manage_Season'))
