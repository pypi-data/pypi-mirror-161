from django.contrib import admin

from .models import Feedback


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("type", "created_on", "author", "archived")
    list_filter = ("type", "archived")
    readonly_fields = ("type", "text", "created_on", "author", "url")


admin.site.register(Feedback, FeedbackAdmin)
