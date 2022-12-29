from django.conf import settings
from django.contrib.auth import models as auth_models

from tanzawa_plugin.exercise.data.strava import models


def is_strava_environment_setup() -> bool:
    return bool(settings.STRAVA_CLIENT_ID and settings.STRAVA_CLIENT_SECRET)


def is_user_connected_to_strava(user: auth_models.User) -> bool:
    return models.Athlete.objects.filter(user=user).exists()
