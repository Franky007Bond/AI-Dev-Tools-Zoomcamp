"""
Settings area authentication.

Access requires a household member with ``Profile.is_admin=True`` and a valid
4-digit PIN. Successful unlock stores the admin profile id in the session.
"""

from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse

from homework_quest.models import Profile

SETTINGS_SESSION_KEY = "settings_profile_id"


class SettingsAuthError(Exception):
    pass


def get_settings_profile(request) -> Profile | None:
    profile_id = request.session.get(SETTINGS_SESSION_KEY)
    if not profile_id:
        return None
    return Profile.objects.filter(pk=profile_id, is_admin=True).first()


def settings_authenticated(request) -> bool:
    return get_settings_profile(request) is not None


def unlock_settings(request, *, profile_id: int, pin: str) -> Profile:
    try:
        profile = Profile.objects.get(pk=profile_id, is_admin=True)
    except Profile.DoesNotExist as exc:
        raise SettingsAuthError("Admin access required.") from exc
    if not profile.check_pin(pin):
        raise SettingsAuthError("Invalid PIN.")
    request.session[SETTINGS_SESSION_KEY] = profile.pk
    return profile


def logout_settings(request) -> None:
    request.session.pop(SETTINGS_SESSION_KEY, None)


def settings_auth_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not settings_authenticated(request):
            return redirect(reverse("settings"))
        return view_func(request, *args, **kwargs)

    return wrapper
