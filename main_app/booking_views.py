import json
import math
from datetime import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def Booking_home(request):
    Booking = get_object_or_404(Booking, admin=request.user)
    total_Car = Car.objects.filter(role=Booking.role).count()
    total_attendance = AttendanceReport.objects.filter(Booking=Booking).count()
    total_present = AttendanceReport.objects.filter(Booking=Booking, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    Car_name = []
    data_present = []
    data_absent = []
    Cars = Car.objects.filter(role=Booking.role)
    for Car in Cars:
        attendance = Attendance.objects.filter(Car=Car)
        present_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=True, Booking=Booking).count()
        absent_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=False, Booking=Booking).count()
        Car_name.append(Car.name)
        data_present.append(present_count)
        data_absent.append(absent_count)
    context = {
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_Car': total_Car,
        'Cars': Cars,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': Car_name,
        'page_title': 'Booking Homepage'

    }
    return render(request, 'Booking_template/home_content.html', context)

def fetch_booking_result(request):
    """
    A view to fetch booking results and return as JSON response.
    """
    # Assuming you want to fetch all booking results for the current user
    current_user = request.user
    booking_results = BookingResult.objects.filter(booking__admin=current_user)
    
    # Serialize booking results into JSON format
    results_data = []
    for booking_result in booking_results:
        result_data = {
            'booking_id': booking_result.booking.id,
            # Add other fields from BookingResult model as needed
        }
        results_data.append(result_data)
    
    # Return JSON response
    return JsonResponse({'booking_results': results_data})


@ csrf_exempt
def Booking_view_attendance(request):
    Booking = get_object_or_404(Booking, admin=request.user)
    if request.method != 'POST':
        role = get_object_or_404(role, id=Booking.role.id)
        context = {
            'Cars': Car.objects.filter(role=role),
            'page_title': 'View Attendance'
        }
        return render(request, 'Booking_template/Booking_view_attendance.html', context)
    else:
        Car_id = request.POST.get('Car')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            Car = get_object_or_404(Car, id=Car_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), Car=Car)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, Booking=Booking)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None




def Booking_feedback(request):
    form = FeedbackBookingForm(request.POST or None)
    Booking = get_object_or_404(Booking, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackBooking.objects.filter(Booking=Booking),
        'page_title': 'Booking Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.Booking = Booking
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('Booking_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "Booking_template/Booking_feedback.html", context)


def Booking_view_profile(request):
    Booking = get_object_or_404(Booking, admin=request.user)
    form = BookingEditForm(request.POST or None, request.FILES or None,
                           instance=Booking)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = Booking.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                Booking.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('Booking_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "Booking_template/Booking_view_profile.html", context)


@csrf_exempt
def Booking_fcmtoken(request):
    token = request.POST.get('token')
    Booking_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        Booking_user.fcm_token = token
        Booking_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def Booking_view_notification(request):
    Booking = get_object_or_404(Booking, admin=request.user)
    notifications = NotificationBooking.objects.filter(Booking=Booking)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "Booking_template/Booking_view_notification.html", context)


def Booking_result(request):
    Booking = get_object_or_404(Booking, admin=request.user)
    results = BookingResult.objects.filter(Booking=Booking)
    context = {
        'results': results,
        'page_title': "View Results"
    }
    return render(request, "Booking_template/Booking_view_result.html", context)
