from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    DEPARTMENT = (
        (1, _('D1')),
        (2, _('D2')),
        (3, _('IT'))
      )
    user = models.OneToOneField(User, verbose_name=_('User'), on_delete=models.CASCADE)
    department = models.IntegerField(_('Department'), choices=DEPARTMENT, default=1)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return f'{self.user}'
