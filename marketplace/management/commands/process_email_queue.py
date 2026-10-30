"""
Django management command to process and retry pending queued emails
from the database email queue, tracking attempt counts and failure logs.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils import timezone

from marketplace.models import EmailQueue


class Command(BaseCommand):
    """Management command to process pending emails in the EmailQueue."""
    
    help = "Processes and retries pending queued emails."

    def handle(self, *args, **options):
        """Execute the command logic to fetch pending emails and dispatch them via mail backend."""
        pending_emails = EmailQueue.objects.filter(
            status=EmailQueue.Status.PENDING,
            retry_count__lt=F("max_retries"),
        )

        if not pending_emails.exists():
            self.stdout.write("No pending emails to process.")
            return

        for email in pending_emails:
            try:
                # Build arguments dynamically to support optional HTML bodies
                kwargs = {
                    "subject": email.subject,
                    "message": email.body_text,
                    "from_email": settings.DEFAULT_FROM_EMAIL,
                    "recipient_list": [email.recipient_email],
                    "fail_silently": False,
                }
                
                if hasattr(email, "body_html") and email.body_html:
                    kwargs["html_message"] = email.body_html

                send_mail(**kwargs)

                email.status = EmailQueue.Status.SENT
                email.last_attempt = timezone.now()
                email.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully sent email #{email.id} to {email.recipient_email}"
                    )
                )

            except Exception as exc:
                email.retry_count += 1
                email.last_attempt = timezone.now()
                email.error_log = str(exc)
                if email.retry_count >= email.max_retries:
                    email.status = EmailQueue.Status.FAILED
                
                email.save()
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed retry ({email.retry_count}/{email.max_retries}) for email #{email.id}: {exc}"
                    )
                )
