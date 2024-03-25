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


def Inquiry_home(request):
    Inquiry = get_object_or_404(Inquiry, admin=request.user)
    total_Car = Car.objects.filter(role=Inquiry.role).count()
    total_attendance = AttendanceReport.objects.filter(Inquiry=Inquiry).count()
    total_present = AttendanceReport.objects.filter(Inquiry=Inquiry, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    Car_name = []
    data_present = []
    data_absent = []
    Cars = Car.objects.filter(role=Inquiry.role)
    for Car in Cars:
        attendance = Attendance.objects.filter(Car=Car)
        present_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=True, Inquiry=Inquiry).count()
        absent_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=False, Inquiry=Inquiry).count()
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
        'page_title': 'Inquiry Homepage'

    }
    return render(request, 'Inquiry_template/home_content.html', context)


@ csrf_exempt
def Inquiry_view_attendance(request):
    Inquiry = get_object_or_404(Inquiry, admin=request.user)
    if request.method != 'POST':
        role = get_object_or_404(role, id=Inquiry.role.id)
        context = {
            'Cars': Car.objects.filter(role=role),
            'page_title': 'View Attendance'
        }
        return render(request, 'Inquiry_template/Inquiry_view_attendance.html', context)
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
                attendance__in=attendance, Inquiry=Inquiry)
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


def Inquiry_apply_leave(request):
    form = LeaveReportInquiryForm(request.POST or None)
    Inquiry = get_object_or_404(Inquiry, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportInquiry.objects.filter(Inquiry=Inquiry),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.Inquiry = Inquiry
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('Inquiry_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "Inquiry_template/Inquiry_apply_leave.html", context)


def Inquiry_feedback(request):
    form = FeedbackInquiryForm(request.POST or None)
    Inquiry = get_object_or_404(Inquiry, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackInquiry.objects.filter(Inquiry=Inquiry),
        'page_title': 'Inquiry Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.Inquiry = Inquiry
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('Inquiry_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "Inquiry_template/Inquiry_feedback.html", context)


def Inquiry_view_profile(request):
    Inquiry = get_object_or_404(Inquiry, admin=request.user)
    form = InquiryEditForm(request.POST or None, request.FILES or None,
                           instance=Inquiry)
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
                admin = Inquiry.admin
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
                Inquiry.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('Inquiry_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "Inquiry_template/Inquiry_view_profile.html", context)


@csrf_exempt
def Inquiry_fcmtoken(request):
    token = request.POST.get('token')
    Inquiry_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        Inquiry_user.fcm_token = token
        Inquiry_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def Inquiry_view_notification(request):
    Inquiry = get_object_or_404(Inquiry, admin=request.user)
    notifications = NotificationInquiry.objects.filter(Inquiry=Inquiry)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "Inquiry_template/Inquiry_view_notification.html", context)


def Inquiry_view_result(request):
    Inquiry = get_object_or_404(Inquiry, admin=request.user)
    results = InquiryResult.objects.filter(Inquiry=Inquiry)
    context = {
        'results': results,
        'page_title': "View Results"
    }
    return render(request, "Inquiry_template/Inquiry_view_result.html", context)
