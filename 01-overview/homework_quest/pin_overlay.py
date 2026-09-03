"""Shared context for the global PIN security overlay."""

from homework_quest.models import Profile


def build_pin_overlay_context() -> dict:
    profiles = Profile.objects.order_by("name")
    return {
        "pin_profiles": profiles,
    }
