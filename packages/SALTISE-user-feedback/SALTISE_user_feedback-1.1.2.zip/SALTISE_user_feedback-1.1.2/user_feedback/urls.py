from django.urls import re_path

from . import views

app_name = "user_feedback"


def patterns():
    return [re_path(r"^post", views.post_feedback_json, name="post")]


urlpatterns = sum([patterns()], [])
