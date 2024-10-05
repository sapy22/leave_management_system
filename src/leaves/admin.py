from django.contrib import admin
from .models import LeaveRequest, LeaveApproval, LeaveBalance


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'approval_stage', 'employee', 'leave_type', 'leave_balance_num', 'from_date', 'to_date', 'days', 'comment', 'officer', 'created_at')
    list_filter = ('employee', 'officer', 'status', 'approval_stage', 'created_at')


@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ('id', 'leave_request', 'stage', 'status', 'approver', 'comment', 'created_at', 'updated_at')
    list_filter = ('approver', 'stage', 'status')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'leave_type', 'comment', 'end_date', 'balance', 'created_at', 'updated_at')
    list_filter = ('employee', 'leave_type', 'created_at')
    search_fields = ['employee__username']
