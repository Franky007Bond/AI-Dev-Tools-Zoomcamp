"""Household settings page context."""

from homework_quest.models import ChoreTemplate, Perk, Profile
from homework_quest.settings_auth import get_settings_profile, settings_authenticated


def build_settings_gate_context(*, error: str = "") -> dict:
    return {
        "admin_profiles": Profile.objects.filter(is_admin=True).order_by("name"),
        "error": error,
    }


def build_settings_context(request) -> dict:
    return {
        "authenticated": True,
        "settings_user": get_settings_profile(request),
        "members": Profile.objects.order_by("name"),
        "perks": Perk.objects.order_by("title"),
        "templates": ChoreTemplate.objects.order_by("title"),
    }
