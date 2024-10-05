import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Permission
from django.db.models import Q

from .models import LeaveRequest, LeaveBalance, LEAVE_TYPE


class LeaveRequestCreateForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ('leave_type', 'leave_balance_num', 'from_date', 'to_date', 'comment', 'officer')
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'leave_balance_num': forms.Select(attrs={'class': 'form-control'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
            'officer': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        self.reg = kwargs.pop("request")
        super().__init__(*args, **kwargs)

        user_department = self.reg.user.profile.department
        self.fields['officer'].queryset = User.objects.filter(
            Q(user_permissions__codename='Officer') |
            Q(groups__permissions__codename='Officer')).filter(
                profile__department=user_department).distinct()
        today = datetime.date.today()
        self.fields['leave_balance_num'].queryset = LeaveBalance.objects.filter(employee=self.reg.user, balance__gt=0, end_date__gte=today)

    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get('leave_type')
        leave_balance_obj: LeaveBalance = cleaned_data.get('leave_balance_num')
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')

        if not (from_date and to_date):
            raise ValidationError(_('Please enter the start and end dates!'))

        if not (to_date >= from_date):
            self.add_error('to_date', ValidationError(_('The end date should be equal to or later than the start date!')))
            return

        if leave_type == 2:
            return

        if not leave_balance_obj:
            self.add_error('leave_balance_num', ValidationError(_('Please select the leave balance number!')))
            return

        if not leave_balance_obj.is_balance_valid(self.reg.user, leave_type):
            self.add_error('leave_balance_num', ValidationError(_('The leave type and balance type do not match!')))
            return

        leave_days = (to_date - from_date).days + 1
        if not leave_balance_obj.is_balance_enough(leave_days):
            raise ValidationError(_('The balance is not enough!'))


class LeaveRequestUpdateForm1(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ('from_date', 'to_date', 'comment')
        widgets = {
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
            }

    def clean(self):
        cleaned_data = super().clean()

        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')

        if not (from_date and to_date):
            raise ValidationError(_('Please enter the start and end dates!'))

        if not (to_date >= from_date):
            self.add_error('to_date', ValidationError(_('The end date should be equal to or later than the start date!')))
            return

        new_leave_days = (to_date - from_date).days + 1

        leave_balance_obj: LeaveBalance = self.instance.leave_balance_num

        if not leave_balance_obj.is_balance_enough_after_restore(self.instance.days, new_leave_days):
            raise ValidationError(_('Not enough balance!'))


class LeaveRequestUpdateForm2(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ('to_date', 'comment')
        widgets = {
            'to_date': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        today = datetime.date.today()

        from_date = self.instance.from_date
        to_date = cleaned_data.get('to_date')

        if not to_date:
            self.add_error('to_date', ValidationError(_('Please enter the end date!')))
            return

        if not (to_date >= today):
            self.add_error('to_date', ValidationError(_('The end date should be equal to or later than today!')))
            return

        new_leave_days = (to_date - from_date).days + 1

        leave_balance_obj: LeaveBalance = self.instance.leave_balance_num

        if not leave_balance_obj.is_balance_enough_after_restore(self.instance.days, new_leave_days):
            raise ValidationError(_('Not enough balance!'))


class LeaveApprovalForm(forms.Form):
    comment = forms.CharField(required=False,widget=forms.Textarea(attrs={'class':'form-control'}))


class LeaveBalanceCreateForm(forms.ModelForm):
    class Meta:
        model = LeaveBalance
        fields = ('employee', 'leave_type', 'comment', 'balance', 'end_date')
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['leave_type'].choices = [choice for choice in LEAVE_TYPE if choice[0] != 2]  # filter out sickleave

    def clean(self):
        cleaned_data = super().clean()

        balance = cleaned_data.get('balance')
        if balance <= 0:
            self.add_error('balance', ValidationError(_('The balance amount must be greater than zero.')))
