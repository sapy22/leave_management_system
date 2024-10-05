import datetime
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


LEAVE_TYPE = (
            (1, _('Annual Leave')),
            (2, _('Sick Leave')),
            (3, _('R1 Leave')),
            (4, _('R2 Leave'))
        )

APPROVAL_STAGES = (
        (1, _('Officer')),
        (2, _('Manager'))
    )


class LeaveRequest(models.Model):
    STATUS = (
            (1, _('Pending')),
            (2, _('Approved')),
            (3, _('Rejected')),
            (4, _('Canceled')),
            (5, _('Modified'))
        )
    status = models.IntegerField(_('Request Status'), choices=STATUS, default=1)
    approval_stage = models.IntegerField(_('Approval Stage'), choices=APPROVAL_STAGES, default=1)
    leave_type = models.IntegerField(_('Leave Type'), choices=LEAVE_TYPE)
    employee = models.ForeignKey(User, verbose_name=_('Employee'), on_delete=models.CASCADE)
    leave_balance_num = models.ForeignKey('LeaveBalance', verbose_name=_('Leave Balance Number'), blank=True, null=True, on_delete=models.CASCADE)  # only if leave_type != sick leave
    from_date = models.DateField(_('From Date'))
    to_date = models.DateField(_('To Date'))
    days = models.PositiveIntegerField(_('Days'))
    comment = models.CharField(_('Comment'), max_length=50, default='', blank=True)
    officer = models.ForeignKey(User, verbose_name=_('Officer'), related_name="leave_reguest_officer", on_delete=models.CASCADE)   # filter officer by department
    original_request = models.ForeignKey('LeaveRequest', verbose_name=_('original request'), blank=True, null=True, on_delete=models.CASCADE)  # if status == modified
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _("Leave Request")
        verbose_name_plural = _("Leave Requests")
        permissions = (("HR", "hr - view leaves"),)
        constraints = [
            models.UniqueConstraint(fields=["employee", "leave_type", "from_date", "to_date", "officer"], name='unique_leaverequest'),
        ]

    def __str__(self):
        return f'{self.id}'

    def get_absolute_url(self):
        return reverse('leave_request_detail', args=[self.id])

    def set_approved(self):
        if self.is_in_process():
            self.status = 2

    def set_rejected(self):
        if self.is_in_process():
            self.status = 3

    def set_cancelled(self):
        if self.is_in_process():
            self.status = 4

    def set_modified(self):
        if self.is_approved():
            self.status = 5

    def set_next_approval_stage(self):
        if self.is_in_approval_stage_1():
            self.approval_stage = 2

    def can_cancel(self):  # check to enable user to cancel the request (in view/template)
        return self.is_in_process()

    def can_update(self):  # check to enable user to update the request (in view/template)
        return self.is_approved() and (datetime.date.today() <= self.to_date) and (not self.is_sickleave())

    def is_in_process(self):
        return self.status == 1

    def is_in_leave(self):  # same as is_actve (in form)
        today = datetime.date.today()
        return today >= self.from_date

    def is_approved(self):
        return self.status == 2

    def is_canceled(self):
        return self.status == 4

    def is_modified(self):
        return self.status == 5

    def is_in_approval_stage_1(self):
        return self.approval_stage == 1

    def is_new(self):
        return self.original_request is None

    def is_sickleave(self):
        return self.leave_type == 2


class LeaveApproval(models.Model):
    STATUS = (
            (1, _('Approved')),  # officer = increase leaverequest stage, manager = update leaverequest status to approved
            (2, _('Rejected'))  # update leaverequest status to rejected
    )
    status = models.IntegerField(_('Approval status'), choices=STATUS)
    stage = models.IntegerField(_('stage'), choices=APPROVAL_STAGES)
    leave_request = models.ForeignKey(LeaveRequest, verbose_name=_('Leave Request Id'), on_delete=models.CASCADE)
    approver = models.ForeignKey(User, verbose_name=_('Approver'), on_delete=models.CASCADE)
    comment = models.CharField(_('Comment'), max_length=50, default='', blank=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _("Leave Approval")
        verbose_name_plural = _("Leave Approvals")
        permissions = (("Officer", "officer - approve stage 1 request"), ("Manager", "manager - approve stage 2 request"))

    def __str__(self):
        return f'{self.id}'


class LeaveBalance(models.Model):
    employee = models.ForeignKey(User, verbose_name=_('Employee'), on_delete=models.CASCADE)
    leave_type = models.IntegerField(_('Leave Type'), choices=LEAVE_TYPE)
    comment = models.CharField(_('Comment'), max_length=50, default='', blank=True)
    end_date = models.DateField(_('End Date'))
    balance = models.PositiveIntegerField(_('Balance'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _("Leave Balance")
        verbose_name_plural = _("Leave Balances")
        permissions = (("Balance_Manager", "balance_manager - manage leave balances"),)
        constraints = [
            models.UniqueConstraint(fields=["employee", "leave_type", "end_date"], name='unique_leavebalance'),
        ]

    def __str__(self):
        v = _('Balance')
        return f'{self.id} - ({self.get_leave_type_display()} - {v}: {self.balance})'

    def add_balance(self, amount):
        """Adds the specified amount to the current balance."""
        self.balance += amount

    def deduct_balance(self, amount):
        """Deducts the specified amount from the current balance."""
        self.balance -= amount

    def add_and_deduct_balance(self, add_amount, deduct_amount):
        """Adds the add_amount to the current balance, then deducts the deduct_amount from the current balance.

        Args:
            add_amount (int): old leave days
            deduct_amount (int): new leave days
        """
        self.add_balance(add_amount)
        self.deduct_balance(deduct_amount)

    def is_active(self):
        today = datetime.date.today()
        return (self.balance > 0) and (self.end_date >= today)

    def is_balance_valid(self, user, leave_type) -> bool:  # check if a valid balance (in form)
        return (self.employee == user) and (self.leave_type == leave_type) and self.is_active

    def is_balance_enough(self, deduct_amount) -> bool:  # check if enough balance (in form)
        return self.balance - deduct_amount >= 0

    def is_balance_enough_after_restore(self, restore_amount, deduct_amount) -> bool:  # check if enough balance (in update form)
        """_summary_

        Args:
            restore_amount (int): old leave days
            deduct_amount (int): leave days

        Returns:
            bool: _description_
        """
        restored_balance = self.balance + restore_amount
        return restored_balance - deduct_amount >= 0
