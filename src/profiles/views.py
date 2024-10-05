from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from secrets import SystemRandom

from .models import Profile
from .forms import EmailChangeForm, EmailVerifyForm


@login_required
def profileIndex(request):
    profile = Profile.objects.get(user=request.user)

    context = {
        "profile": profile,
    }
    return render(request, "profiles/profile_index.html", context)


@login_required
def emailChange(request):
    if request.method == "POST":
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            random_obj = SystemRandom()
            passcode = random_obj.randrange(100000, 999999)

            request.session["email_change_passcode"] = passcode
            request.session["email_change_new_email"] = email

            subj = _("Email Reset")
            msg = _("This is your passcode:")

            send_mail(
                subj,
                f"{msg} {passcode}",
                "",
                [
                    email,
                ],
                fail_silently=True,
            )

            return redirect("email_verify")
    else:
        form = EmailChangeForm()

    context = {
        "form": form,
    }

    return render(request, "profiles/profile_email_change_form.html", context)


@login_required
def emailVerify(request):
    email_change_passcode = request.session.get("email_change_passcode", None)
    email_change_new_email = request.session.get("email_change_new_email", None)

    if not (email_change_passcode and email_change_new_email):
        return redirect("profile_index")

    if request.method == "POST":
        form = EmailVerifyForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=request.user)

            code = form.cleaned_data["code"]
            passcode = email_change_passcode
            passcode = str(passcode)

            if code == passcode:
                user.email = email_change_new_email
                user.save()
                messages.add_message(request, messages.SUCCESS, _("Success"))
            else:
                messages.add_message(request, messages.ERROR, _("Error"))
            try:
                del request.session["email_change_passcode"]
                del request.session["email_change_new_email"]
            except:
                pass
            return redirect("profile_index")
    else:
        form = EmailVerifyForm()

    context = {
        "form": form,
    }

    return render(request, "profiles/profile_email_verify_form.html", context)
