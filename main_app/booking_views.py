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


def booking_home(request):
    booking = get_object_or_404(booking, admin=request.user)
    total_Car = Car.objects.filter(role=booking.role).count()
    total_trips = tripsReport.objects.filter(booking=booking).count()
    total_present = tripsReport.objects.filter(booking=booking, status=True).count()
    if total_trips == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_trips) * 100)
        percent_absent = math.ceil(100 - percent_present)
    Car_name = []
    data_present = []
    data_absent = []
    Cars = Car.objects.filter(role=booking.role)
    for Car in Cars:
        trips = trips.objects.filter(Car=Car)
        present_count = tripsReport.objects.filter(
            trips__in=trips, status=True, booking=booking).count()
        absent_count = tripsReport.objects.filter(
            trips__in=trips, status=False, booking=booking).count()
        Car_name.append(Car.name)
        data_present.append(present_count)
        data_absent.append(absent_count)
    context = {
        'total_trips': total_trips,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_Car': total_Car,
        'Cars': Cars,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': Car_name,
        'page_title': 'booking Homepage'

    }
    return render(request, 'booking_template/home_content.html', context)


@ csrf_exempt
def booking_view_trips(request):
    booking = get_object_or_404(booking, admin=request.user)
    if request.method != 'POST':
        role = get_object_or_404(role, id=booking.role.id)
        context = {
            'Cars': Car.objects.filter(role=role),
            'page_title': 'View trips'
        }
        return render(request, 'booking_template/booking_view_trips.html', context)
    else:
        Car_id = request.POST.get('Car')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            Car = get_object_or_404(Car, id=Car_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            trips = trips.objects.filter(
                date__range=(start_date, end_date), Car=Car)
            trips_reports = tripsReport.objects.filter(
                trips__in=trips, booking=booking)
            json_data = []
            for report in trips_reports:
                data = {
                    "date":  str(report.trips.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None


def booking_apply_leave(request):
    form = LeaveReportbookingForm(request.POST or None)
    booking = get_object_or_404(booking, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportbooking.objects.filter(booking=booking),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.booking = booking
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('booking_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "booking_template/booking_apply_leave.html", context)


def booking_feedback(request):
    form = FeedbackbookingForm(request.POST or None)
    booking = get_object_or_404(booking, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': Feedbackbooking.objects.filter(booking=booking),
        'page_title': 'booking Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.booking = booking
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('booking_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "booking_template/booking_feedback.html", context)


def booking_view_profile(request):
    booking = get_object_or_404(booking, admin=request.user)
    form = bookingEditForm(request.POST or None, request.FILES or None,
                           instance=booking)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                # address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = booking.admin
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                # admin.address = address
                admin.gender = gender
                admin.save()
                booking.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('booking_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "booking_template/booking_view_profile.html", context)


@csrf_exempt
def booking_fcmtoken(request):
    token = request.POST.get('token')
    booking_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        booking_user.fcm_token = token
        booking_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def booking_view_notification(request):
    booking = get_object_or_404(booking, admin=request.user)
    notifications = Notificationbooking.objects.filter(booking=booking)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "booking_template/booking_view_notification.html", context)


def booking_view_result(request):
    booking = get_object_or_404(booking, admin=request.user)
    results = bookingResult.objects.filter(booking=booking)
    context = {
        'results': results,
        'page_title': "View Results"
    }
    return render(request, "booking_template/booking_view_result.html", context)
