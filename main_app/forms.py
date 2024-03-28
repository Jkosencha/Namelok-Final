from django import apps, forms
from django.apps import apps
from .models import CustomUser, booking, Admin, Staff, Role, Car, Season, LeaveReportStaff, FeedbackStaff, LeaveReportbooking, Feedbackbooking, bookingResult
from django.forms.widgets import DateInput, TextInput
from django import forms

from .models import Role

from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        CustomUser = apps.get_model('main_app', 'CustomUser')

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender',  'password','profile_pic', 'address' ]


class BookingForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = booking
        fields = ['first_name', 'last_name', 'email', 'gender', 'season']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['role' ]


class roleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name']

class CarForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(CarForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Car
        fields = ['name', 'staff', 'role']


class SeasonForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SeasonForm, self).__init__(*args, **kwargs)
        Season = apps.get_model('main_app', 'Season')

    class Meta:
        model = Season
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class LeaveReportbookingForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportbookingForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportbooking
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackbookingForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackbookingForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Feedbackbooking
        fields = ['feedback']


class bookingEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(bookingEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = booking
        fields = CustomUserForm.Meta.fields 


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


class EditResultForm(FormSettings):
    Season_list = Season.objects.all()
    Season_year = forms.ModelChoiceField(
        label="Season Year", queryset=Season_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = bookingResult
        fields = ['Season_year', 'Car', 'booking', 'test', 'exam']
