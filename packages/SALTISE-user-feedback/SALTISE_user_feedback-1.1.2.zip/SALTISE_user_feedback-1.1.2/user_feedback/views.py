import json
from datetime import datetime, timedelta, timezone

from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Feedback
from .serializers import FeedbackSerializer


@require_POST
@login_required
def post_feedback_json(request):
    data = json.loads(request.body)
    serializer = FeedbackSerializer(data=data)
    if serializer.is_valid():
        feedback_object = serializer.save(author=request.user)
        if feedback_object.type == 1:
            send_bug_report_emails(request, feedback_object)
        response = JsonResponse({"detail": "success"})
        response.status_code = 201
        return response
    else:
        response = JsonResponse({"detail": "error"})
        response.status_code = 400
        return response


def send_bug_report_emails(request, feedback_object):
    mail_admins(
        subject="URGENT - bug report",
        message="A bug has been reported on %s's %s. The user has written the "
        "following: '%s' There have been %d other bugs reported in the "
        "last 10 days at this url."
        % (
            request.get_host(),
            feedback_object.url[1:-1],
            feedback_object.text,
            Feedback.objects.filter(
                type=1,
                url=feedback_object.url,
                created_on__lte=datetime.now(timezone.utc),
                created_on__gt=datetime.now(timezone.utc) - timedelta(days=10),
            ).count()
            - 1,
        ),
        fail_silently=False,
    )
