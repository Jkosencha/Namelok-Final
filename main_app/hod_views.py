import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from main_app import inquiry_views

from .forms import *
from .models import *


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_inquiries = Inquiry.objects.all().count()
    all_Cars = Car.objects.all()
    total_Car = all_Cars.count()
    total_role = Role.objects.all().count()
    attendance_list = Attendance.objects.filter(Car__in=all_Cars)
    total_attendance = attendance_list.count()
    attendance_list = []
    Car_list = []
    for car_instance in all_Cars:
        attendance_count = Attendance.objects.filter(Car=car_instance).count()
        Car_list.append(car_instance.name[:7])
        attendance_list.append(attendance_count)

    # Total Cars and inquiries in Each role
    all_roles = Role.objects.all()
    role_name_list = []
    Car_count_list = []
    inquiry_count_list_in_role = []

    for role in all_roles:
        Cars = Car.objects.filter(role_id=role.id).count()
        inquiries = Inquiry.objects.filter(role_id=role.id).count()
        role_name_list.append(role.name)
        Car_count_list.append(Cars)
        inquiry_count_list_in_role.append(inquiries)
    
    all_Cars = Car.objects.all()
    Car_list = []
    inquiry_count_list_in_Car = []
    for car_instance in all_Cars:
        role = role.objects.get(id=car_instance.role.id)
        inquiry_count = Inquiry.objects.filter(role_id=role.id).count()
        Car_list.append(car_instance.name)
        inquiry_count_list_in_Car.append(inquiry_count)



    # For inquiries
    inquiry_attendance_present_list = []
    inquiry_attendance_leave_list = []
    inquiry_name_list = []

    inquiries = Inquiry.objects.all()
    for inquiry in inquiries:
        
        attendance = AttendanceReport.objects.filter(inquiry_id=inquiry.id, status=True).count()
        absent = AttendanceReport.objects.filter(inquiry_id=inquiry.id, status=False).count()
        leave = LeaveReportInquiry.objects.filter(inquiry_id=inquiry.id, status=1).count()
        inquiry_attendance_present_list.append(attendance)
        inquiry_attendance_leave_list.append(leave + absent)
        inquiry_name_list.append(inquiry.admin.first_name)

    context = {
        'page_title': "Administrative Dashboard",
        'total_inquiries': total_inquiries,
        'total_staff': total_staff,
        'total_role': total_role,
        'total_Car': total_Car,
        'Car_list': Car_list,
        'attendance_list': attendance_list,
        'inquiry_attendance_present_list': inquiry_attendance_present_list,
        'inquiry_attendance_leave_list': inquiry_attendance_leave_list,
        "inquiry_name_list": inquiry_name_list,
        "inquiry_count_list_in_Car": inquiry_count_list_in_Car,
        "inquiry_count_list_in_role": inquiry_count_list_in_role,
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
            password = form.cleaned_data.get('password')
            role = form.cleaned_data.get('role')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.staff.role = role
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_Inquiry(request):
    Inquiry_form = InquiryForm(request.POST or None, request.FILES or None)
    context = {'form': Inquiry_form, 'page_title': 'Add Inquiry'}
    if request.method == 'POST':
        if Inquiry_form.is_valid():
            first_name = Inquiry_form.cleaned_data.get('first_name')
            last_name = Inquiry_form.cleaned_data.get('last_name')
            address = Inquiry_form.cleaned_data.get('address')
            email = Inquiry_form.cleaned_data.get('email')
            gender = Inquiry_form.cleaned_data.get('gender')
            password = Inquiry_form.cleaned_data.get('password')
            role = Inquiry_form.cleaned_data.get('role')
            Season = Inquiry_form.cleaned_data.get('Season')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.Inquiry.Season = Season
                user.Inquiry.role = role
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_Inquiry'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_Inquiry_template.html', context)

def add_Booking(request):
    Booking_form = BookingForm(request.POST or None, request.FILES or None)
    context = {'form': Booking_form, 'page_title': 'Add Booking'}
    if request.method == 'POST':
        if Booking_form.is_valid():
            first_name = Booking_form.cleaned_data.get('first_name')
            last_name = Booking_form.cleaned_data.get('last_name')
            address = Booking_form.cleaned_data.get('address')
            email = Booking_form.cleaned_data.get('email')
            gender = Booking_form.cleaned_data.get('gender')
            car = Booking_form.cleaned_data.get('car')
            Season = Booking_form.cleaned_data.get('Season')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, user_type=3, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.Booking.Season = Season
                user.Booking.car = car
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_Booking'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_Booking_template.html', context)




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
                role = role()
                role.name = name
                role.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_role'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_role_template.html', context)


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
                Car = Car()
                Car.name = name
                Car.staff = staff
                Car.role = role
                Car.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_Car'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_Car_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Staff'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_Inquiry(request):
    inquiries = CustomUser.objects.filter(user_type=3)
    context = {
        'inquiries': inquiries,
        'page_title': 'Manage inquiries'
    }
    return render(request, "hod_template/manage_Inquiry.html", context)

def manage_Booking(request):
    bookings = CustomUser.objects.filter(user_type=3)
    context = {
        'bookings': bookings,
        'page_title': 'Manage bookings'
    }
    return render(request, "hod_template/manage_Booking.html", context)


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


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Staff'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            role = form.cleaned_data.get('role')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                staff.role = role
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=staff_id)
        staff = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_Inquiry(request, Inquiry_id):
    Inquiry = get_object_or_404(Inquiry, id=Inquiry_id)
    form = InquiryForm(request.POST or None, instance=Inquiry)
    context = {
        'form': form,
        'Inquiry_id': Inquiry_id,
        'page_title': 'Edit Inquiry'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            role = form.cleaned_data.get('role')
            Season = form.cleaned_data.get('Season')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=Inquiry.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                Inquiry.Season = Season
                user.gender = gender
                user.address = address
                Inquiry.role = role
                user.save()
                Inquiry.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_Inquiry', args=[Inquiry_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_Inquiry_template.html", context)


def edit_role(request, role_id):
    instance = get_object_or_404(role, id=role_id)
    form = roleForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'role_id': role_id,
        'page_title': 'Edit role'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                role = role.objects.get(id=role_id)
                role.name = name
                role.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
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
    Season = Season.objects.all()
    context = {'Season': Season, 'page_title': 'Manage Season'}
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
def Inquiry_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackInquiry.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Inquiry Feedback Messages'
        }
        return render(request, 'hod_template/Inquiry_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackInquiry, id=feedback_id)
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
def view_Inquiry_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportInquiry.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From inquiries'
        }
        return render(request, "hod_template/Inquiry_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportInquiry, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    Cars = Car.objects.all()
    Season = Season.objects.all()
    context = {
        'Cars': Cars,
        'Season': Season,
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    Car_id = request.POST.get('Car')
    Season_id = request.POST.get('Season')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        Car = get_object_or_404(Car, id=Car_id)
        Season = get_object_or_404(Season, id=Season_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, Season=Season)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.Inquiry)
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


def admin_notify_Inquiry(request):
    Inquiry = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To inquiries",
        'inquiries': Inquiry
    }
    return render(request, "hod_template/Inquiry_notification.html", context)


@csrf_exempt
def send_Inquiry_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    Inquiry = get_object_or_404(Inquiry, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Inquiry Management System",
                'body': message,
                'click_action': reverse('Inquiry_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': Inquiry.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationInquiry(Inquiry=Inquiry, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Inquiry Management System",
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


def delete_Inquiry(request, Inquiry_id):
    Inquiry = get_object_or_404(CustomUser, Inquiry__id=Inquiry_id)
    Inquiry.delete()
    messages.success(request, "Inquiry deleted successfully!")
    return redirect(reverse('manage_Inquiry'))

def delete_Booking(request, Booking_id):
    Booking = get_object_or_404(CustomUser, Boooking__id=Booking_id)
    Booking.delete()
    messages.success(request, "Booking deleted successfully!")
    return redirect(reverse('manage_Booking'))


def delete_role(request, role_id):
    role = get_object_or_404(role, id=role_id)
    try:
        role.delete()
        messages.success(request, "role deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some inquiries are assigned to this role already. Kindly change the affected Inquiry role and try again")
    return redirect(reverse('manage_role'))


def delete_Car(request, Car_id):
    Car = get_object_or_404(Car, id=Car_id)
    Car.delete()
    messages.success(request, "Car deleted successfully!")
    return redirect(reverse('manage_Car'))


def delete_Season(request, Season_id):
    Season = get_object_or_404(Season, id=Season_id)
    try:
        Season.delete()
        messages.success(request, "Season deleted successfully!")
    except Exception:
        messages.error(
            request, "There are inquiries assigned to this Season. Please move them to another Season.")
    return redirect(reverse('manage_Season'))
