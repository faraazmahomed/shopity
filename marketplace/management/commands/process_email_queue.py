from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from marketplace.models import EmailQueue


class Command(BaseCommand):
    help = 'Processes pending background emails from the EmailQueue'

    def handle(self, *args, **options):
        pending_emails = EmailQueue.objects.filter(sent=False, attempts__lt=3)[:20]

        for email in pending_emails:
            try:
                send_mail(
                    subject=email.subject,
                    message=email.message,
                    from_email='no-reply@marketplace.com',
                    recipient_list=[email.to_email],
                    fail_silently=False,
                )
                email.sent = True
                self.stdout.write(self.style.SUCCESS(f"Sent email to {email.to_email}"))
            except Exception as e:
                email.attempts += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed sending to {
                            email.to_email}: {e}"))

            email.last_attempt = timezone.now()
            email.save()
