import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    total_bookings = booking.objects.filter(role=staff.role).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    Cars = Car.objects.filter(staff=staff)
    total_Car = Cars.count()
    trips_list = trips.objects.filter(Car__in=Cars)
    total_trips = trips_list.count()
    trips_list = []
    Car_list = []
    for Car in Cars:
        trips_count = trips.objects.filter(Car=Car).count()
        Car_list.append(Car.name)
        trips_list.append(trips_count)
    context = {
        'page_title': 'Staff Panel - ' + str(staff.admin.last_name) + ' (' + str(staff.role) + ')',
        'total_bookings': total_bookings,
        'total_trips': total_trips,
        'total_leave': total_leave,
        'total_Car': total_Car,
        'Car_list': Car_list,
        'trips_list': trips_list
    }
    return render(request, 'staff_template/home_content.html', context)


def staff_take_trips(request):
    staff = get_object_or_404(Staff, admin=request.user)
    Cars = Car.objects.filter(staff_id=staff)
    Season = Season.objects.all()
    context = {
        'Cars': Cars,
        'Season': Season,
        'page_title': 'Take trips'
    }

    return render(request, 'staff_template/staff_take_trips.html', context)


@csrf_exempt
def get_bookings(request):
    Car_id = request.POST.get('Car')
    Season_id = request.POST.get('Season')
    try:
        Car = get_object_or_404(Car, id=Car_id)
        Season = get_object_or_404(Season, id=Season_id)
        bookings = booking.objects.filter(
            role_id=Car.role.id, Season=Season)
        booking_data = []
        for booking in bookings:
            data = {
                    "id": booking.id,
                    "name": booking.admin.last_name + " " + booking.admin.first_name
                    }
            booking_data.append(data)
        return JsonResponse(json.dumps(booking_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def save_trips(request):
    booking_data = request.POST.get('booking_ids')
    date = request.POST.get('date')
    Car_id = request.POST.get('Car')
    Season_id = request.POST.get('Season')
    bookings = json.loads(booking_data)
    try:
        Season = get_object_or_404(Season, id=Season_id)
        Car = get_object_or_404(Car, id=Car_id)
        trips = trips(Season=Season, Car=Car, date=date)
        trips.save()

        for booking_dict in bookings:
            booking = get_object_or_404(booking, id=booking_dict.get('id'))
            trips_report = tripsReport(booking=booking, trips=trips, status=booking_dict.get('status'))
            trips_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_update_trips(request):
    staff = get_object_or_404(Staff, admin=request.user)
    Cars = Car.objects.filter(staff_id=staff)
    Season = Season.objects.all()
    context = {
        'Cars': Cars,
        'Season': Season,
        'page_title': 'Update trips'
    }

    return render(request, 'staff_template/staff_update_trips.html', context)


@csrf_exempt
def get_booking_trips(request):
    trips_date_id = request.POST.get('trips_date_id')
    try:
        date = get_object_or_404(trips, id=trips_date_id)
        trips_data = tripsReport.objects.filter(trips=date)
        booking_data = []
        for trips in trips_data:
            data = {"id": trips.booking.admin.id,
                    "name": trips.booking.admin.last_name + " " + trips.booking.admin.first_name,
                    "status": trips.status}
            booking_data.append(data)
        return JsonResponse(json.dumps(booking_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_trips(request):
    booking_data = request.POST.get('booking_ids')
    date = request.POST.get('date')
    bookings = json.loads(booking_data)
    try:
        trips = get_object_or_404(trips, id=date)

        for booking_dict in bookings:
            booking = get_object_or_404(
                booking, admin_id=booking_dict.get('id'))
            trips_report = get_object_or_404(tripsReport, booking=booking, trips=trips)
            trips_report.status = booking_dict.get('status')
            trips_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
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
                staff.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    Cars = Car.objects.filter(staff=staff)
    Season = Season.objects.all()
    context = {
        'page_title': 'Result Upload',
        'Cars': Cars,
        'Season': Season
    }
    if request.method == 'POST':
        try:
            booking_id = request.POST.get('booking_list')
            Car_id = request.POST.get('Car')
            test = request.POST.get('test')
            exam = request.POST.get('exam')
            booking = get_object_or_404(booking, id=booking_id)
            Car = get_object_or_404(Car, id=Car_id)
            try:
                data = bookingResult.objects.get(
                    booking=booking, Car=Car)
                data.exam = exam
                data.test = test
                data.save()
                messages.success(request, "Scores Updated")
            except:
                result = bookingResult(booking=booking, Car=Car, test=test, exam=exam)
                result.save()
                messages.success(request, "Scores Saved")
        except Exception as e:
            messages.warning(request, "Error Occured While Processing Form")
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_booking_result(request):
    try:
        Car_id = request.POST.get('Car')
        booking_id = request.POST.get('booking')
        booking = get_object_or_404(booking, id=booking_id)
        Car = get_object_or_404(Car, id=Car_id)
        result = bookingResult.objects.get(booking=booking, Car=Car)
        result_data = {
            'exam': result.exam,
            'test': result.test
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')
