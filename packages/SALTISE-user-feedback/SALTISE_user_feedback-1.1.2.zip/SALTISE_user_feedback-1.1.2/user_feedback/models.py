from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _

User = get_user_model()


class Feedback(models.Model):

    FEEDBACK_TYPE = (
        (1, "Bug Report"),
        (2, "Feature Request"),
        (3, "General Feedback"),
    )

    type = models.PositiveIntegerField(choices=FEEDBACK_TYPE)
    text = models.CharField(max_length=2000)
    url = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(
        help_text=_("Check to mark this comment as resolved."),
        verbose_name=_("archive status"),
        default=False,
    )

    def __str__(self):
        return (
            f"{self.FEEDBACK_TYPE[self.type-1][1]}: '{self.text}' "
            f"by {self.author} at {self.url} on {self.created_on}"
        )

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"
