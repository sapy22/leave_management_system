from django import forms
from django.utils.translation import gettext_lazy as _



class EmailChangeForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"), widget=forms.EmailInput(attrs={"class": "form-control"})
    )


class EmailVerifyForm(forms.Form):
    code = forms.CharField(
        label=_("Code"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
