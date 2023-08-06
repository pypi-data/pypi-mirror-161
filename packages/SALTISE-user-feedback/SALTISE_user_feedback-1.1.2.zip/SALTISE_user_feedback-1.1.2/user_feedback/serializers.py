import bleach
from rest_framework import serializers

from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["author", "text", "type", "url"]

    def create(self, validated_data):
        return Feedback.objects.create(
            author=validated_data["author"],
            text=bleach.clean(
                validated_data["text"], tags=[], strip=True
            ).rstrip(),
            type=validated_data["type"],
            url=validated_data["url"],
        )
