from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


def send_email_employee(leaverequest):
    subject = _('Leave Request Id ') + f'{leaverequest.id}'
    from_email = ''
    to = [leaverequest.employee.email,]

    leaverequest_dict = {'id': leaverequest.id, 'status': leaverequest.get_status_display(),
                         'leave_type': leaverequest.get_leave_type_display(), 'from_date': leaverequest.from_date,
                         'to_date': leaverequest.to_date, 'days': leaverequest.days}

    text_content = render_to_string('leaves/email/email.txt', leaverequest_dict)
    html_content = render_to_string('leaves/email/email.html', leaverequest_dict)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=True)
