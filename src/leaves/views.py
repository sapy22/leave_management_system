import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction, IntegrityError
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import LeaveRequest, LeaveApproval, LeaveBalance
from .forms import LeaveRequestCreateForm, LeaveApprovalForm, LeaveRequestUpdateForm1, LeaveRequestUpdateForm2, LeaveBalanceCreateForm
from .utils import send_email_employee


@login_required
def leaveRequestIndex(request):
    user = request.user
    today = datetime.date.today()

    leave_request = LeaveRequest.objects.filter(employee=user).order_by('-id')

    lr_total_count = len(leave_request)
    lr_approved_count = leave_request.filter(status=2).count()
    lr_rejected_count = leave_request.filter(status=3).count()
    lr_canceled_count = leave_request.filter(status=4).count()

    try:
        leave_balance = user.leavebalance_set.filter(balance__gt=0, end_date__gte=today)
    except AttributeError:
        leave_balance = None

    paginator = Paginator(leave_request, 10)
    page = request.GET.get('page')
    try:
        leave_request = paginator.page(page)
    except PageNotAnInteger:
        leave_request = paginator.page(1)
    except EmptyPage:
        leave_request = paginator.page(paginator.num_pages)

    context = {
        'leave_request': leave_request,
        'lr_total_count': lr_total_count,
        'lr_approved_count': lr_approved_count,
        'lr_rejected_count': lr_rejected_count,
        'lr_canceled_count': lr_canceled_count,
        'leave_balance': leave_balance,
    }

    return render(request, 'leaves/leave_index.html', context)


@login_required
def leaveRequestDetail(request, id):
    user = request.user

    try:
        leave_request = LeaveRequest.objects.get(pk=id)
    except LeaveRequest.DoesNotExist:
        messages.add_message(request, messages.ERROR, _('Error'))
        return redirect('leave_request_index')

    if user != leave_request.employee:
        messages.add_message(request, messages.ERROR, _('Error'))
        return redirect('leave_request_index')

    leave_approval = LeaveApproval.objects.filter(leave_request=leave_request)

    context = {
            'leave_request': leave_request,
            'leave_approval': leave_approval
        }

    return render(request, 'leaves/leave_detail.html', context)


@login_required
def LeaveApprovalIndex(request):
    user = request.user

    if not (user.has_perm('leaves.Officer') or user.has_perm('leaves.Manager')):
        raise PermissionDenied()

    if (user.has_perm('leaves.Officer') and user.has_perm('leaves.Manager')):
        leave_request = LeaveRequest.objects.filter(Q(status=1, approval_stage=1, officer=user) | Q(status=1, approval_stage=2)).order_by('-id')
    elif user.has_perm('leaves.Officer'):
        leave_request = LeaveRequest.objects.filter(status=1, approval_stage=1, officer=user).order_by('-id')
    else:
        leave_request = LeaveRequest.objects.filter(status=1, approval_stage=2).order_by('-id')

    lr_pending_count = leave_request.count()

    paginator = Paginator(leave_request, 5)
    page = request.GET.get('page')
    try:
        leave_request = paginator.page(page)
    except PageNotAnInteger:
        leave_request = paginator.page(1)
    except EmptyPage:
        leave_request = paginator.page(paginator.num_pages)

    context = {
        'leave_request': leave_request,
        'lr_pending_count': lr_pending_count,
    }

    return render(request, 'leaves/leave_approval_index.html', context)


@permission_required('leaves.HR', raise_exception=True)
def leaveActiveIndex(request):
    today = datetime.date.today()

    leave_request = LeaveRequest.objects.filter(from_date__lte=today, to_date__gte=today, status=2).order_by('from_date')

    lr_active_count = len(leave_request)

    paginator = Paginator(leave_request, 10)
    page = request.GET.get('page')
    try:
        leave_request = paginator.page(page)
    except PageNotAnInteger:
        leave_request = paginator.page(1)
    except EmptyPage:
        leave_request = paginator.page(paginator.num_pages)

    context = {
        'leave_request': leave_request,
        'lr_active_count': lr_active_count,
    }

    return render(request, 'leaves/leave_active_index.html', context)


@login_required
def leaveRequestCreate(request):
    if request.method == 'POST':
        form = LeaveRequestCreateForm(request.POST, request=request)
        if form.is_valid():
            try:
                with transaction.atomic():
                    lr_instance = form.save(commit=False)
                    lr_instance.employee = request.user
                    lr_instance.days = (lr_instance.to_date - lr_instance.from_date).days + 1
                    lr_instance.save()

                messages.add_message(request, messages.SUCCESS, _('Success'))
                return redirect(lr_instance)

            except IntegrityError:
                messages.add_message(request, messages.ERROR, _('Error: already exists!'))
                return redirect('leave_request_create')
    else:
        form = LeaveRequestCreateForm(request=request)

    context = {'form': form}

    return render(request, 'leaves/leave_create_form.html', context)


@login_required
def leave_request_cancel(request):
    user = request.user

    if request.method != 'POST':
        raise PermissionDenied()

    id = request.POST.get('leaverequest_id')
    try:
        leaverequest = LeaveRequest.objects.get(id=id)
    except:
        leaverequest = None

    if not (leaverequest and leaverequest.can_cancel() and leaverequest.employee == user):
        raise PermissionDenied()

    if 'cancel' in request.POST:
        leaverequest.set_cancelled()
        leaverequest.save()
        messages.add_message(request, messages.SUCCESS, _('Success'))
        return redirect('leave_request_index')
    else:
        raise PermissionDenied()


@login_required
def leaveRequestUpdate(request, id):
    user = request.user
    frm_date = None
    today = datetime.date.today()

    try:
        leaverequest = LeaveRequest.objects.get(id=id)
    except:
        leaverequest = None

    if not (leaverequest and leaverequest.can_update() and leaverequest.employee == user):
        raise PermissionDenied()

    if (today >= leaverequest.from_date):
        frm_date = leaverequest.from_date

    if request.method == 'POST':
        form = LeaveRequestUpdateForm1(request.POST, instance=leaverequest)
        if (today >= leaverequest.from_date):
            form = LeaveRequestUpdateForm2(request.POST, instance=leaverequest)

        if form.is_valid():
            new_days = (form.instance.to_date - form.instance.from_date).days + 1
            comment = form.cleaned_data.get('comment')

            try:
                new_lr = LeaveRequest.objects.create(
                    leave_type=leaverequest.leave_type, employee=leaverequest.employee, leave_balance_num=leaverequest.leave_balance_num, from_date=leaverequest.from_date, 
                    to_date=leaverequest.to_date, days=new_days, comment=comment, officer=leaverequest.officer, original_request=leaverequest)

                messages.add_message(request, messages.SUCCESS, _('Success'))
                return redirect(new_lr)

            except IntegrityError:
                messages.add_message(request, messages.ERROR, _('Error: already exists!'))
                return redirect('leave_request_update', leaverequest)

    else:
        form = LeaveRequestUpdateForm1(instance=leaverequest)
        if (today >= leaverequest.from_date):
            form = LeaveRequestUpdateForm2(instance=leaverequest)

    context = {'form': form, 'frm_date': frm_date, 'lr_id': leaverequest.id}

    return render(request, 'leaves/leave_update_form.html', context)


@login_required
def leave_approval_create(request):
    user = request.user

    if not (user.has_perm('leaves.Officer') or user.has_perm('leaves.Manager')):
        raise PermissionDenied()

    if request.method != 'POST':
        raise PermissionDenied()

    form = LeaveApprovalForm(request.POST)

    if not form.is_valid():
        raise PermissionDenied()

    id = request.POST.get('leaverequest_id')
    try:
        leaverequest = LeaveRequest.objects.get(id=id)
    except:
        leaverequest = None

    if not (leaverequest and leaverequest.is_in_process()):
        raise PermissionDenied()

    if leaverequest.is_in_approval_stage_1():
        return approve_officer(request, user, leaverequest, form)
    else:
        return approve_manager(request, user, leaverequest, form)


def approve_officer(request, user, leaverequest, form):
    if not (leaverequest.officer == user):
        raise PermissionDenied()

    if 'approve' in request.POST:
        try:
            with transaction.atomic():
                LeaveApproval.objects.create(leave_request=leaverequest, approver=user, stage=1, status=1, comment=form.cleaned_data['comment'])
                leaverequest.set_next_approval_stage()
                leaverequest.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, _('Error'))
            return redirect('leave_approval_index')

    elif 'reject' in request.POST:
        try:
            with transaction.atomic():
                LeaveApproval.objects.create(leave_request=leaverequest, approver=user, stage=1, status=2, comment=form.cleaned_data['comment'])
                leaverequest.set_rejected()
                leaverequest.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, _('Error'))
            return redirect('leave_approval_index')
    else:
        raise PermissionDenied()

    send_email_employee(leaverequest)
    messages.add_message(request, messages.SUCCESS, _('Success'))
    return redirect('leave_approval_index')


def approve_manager(request, user, leaverequest, form):
    if 'approve' in request.POST:
        try:
            with transaction.atomic():
                if leaverequest.is_new():
                    _subtract_days_from_balance(leaverequest)

                    LeaveApproval.objects.create(leave_request=leaverequest, approver=user, stage=2, status=1, comment=form.cleaned_data['comment'])
                    leaverequest.set_approved()
                    leaverequest.save()
                else:
                    _add_and_subtract_days_from_balance(leaverequest)

                    LeaveApproval.objects.create(leave_request=leaverequest, approver=user, stage=2, status=1, comment=form.cleaned_data['comment'])
                    leaverequest.set_approved()
                    leaverequest.save()

                    original_request = leaverequest.original_request
                    original_request.set_modified()
                    original_request.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, _('Error'))
            return redirect('leave_approval_index')

    elif 'reject' in request.POST:
        try:
            with transaction.atomic():
                LeaveApproval.objects.create(leave_request=leaverequest, approver=user, stage=2, status=2, comment=form.cleaned_data['comment'])
                leaverequest.set_rejected()
                leaverequest.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, _('Error'))
            return redirect('leave_approval_index')
    else:
        raise PermissionDenied()

    send_email_employee(leaverequest)
    messages.add_message(request, messages.SUCCESS, _('Success'))
    return redirect('leave_approval_index')


def _subtract_days_from_balance(leave_request: LeaveRequest):
    if not leave_request.is_sickleave():
        balance_obj: LeaveBalance = leave_request.leave_balance_num
        balance_obj.deduct_balance(leave_request.days)
        balance_obj.save()


def _add_and_subtract_days_from_balance(leave_request: LeaveRequest):
    if not leave_request.is_sickleave():
        balance_obj: LeaveBalance = leave_request.leave_balance_num
        balance_obj.add_and_deduct_balance(leave_request.original_request.days, leave_request.days)
        balance_obj.save()


@permission_required('leaves.Balance', raise_exception=True)
def leaveBalanceCreate(request):
    if request.method == 'POST':
        form = LeaveBalanceCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()

                messages.add_message(request, messages.SUCCESS, _('Success'))
                return redirect('leave_balance_create')

            except IntegrityError:
                messages.add_message(request, messages.ERROR, _('Error'))
                return redirect('leave_balance_create')
    else:
        form = LeaveBalanceCreateForm()

    context = {'form': form}

    return render(request, 'leaves/leave_balance_create_form.html', context)
