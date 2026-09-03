from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from homework_quest.models import ChoreTemplate, Perk, Profile
from homework_quest.settings_auth import (
    SettingsAuthError,
    logout_settings,
    settings_auth_required,
    settings_authenticated,
    unlock_settings,
)
from homework_quest.settings_page import build_settings_context, build_settings_gate_context


def settings_view(request):
    if not settings_authenticated(request):
        error = request.GET.get("error", "")
        if error == "pin":
            error = "Invalid PIN or not an admin."
        elif error == "auth":
            error = "Admin sign-in required."
        else:
            error = ""
        return render(
            request,
            "homework_quest/settings_gate.html",
            build_settings_gate_context(error=error),
        )
    return render(request, "homework_quest/settings.html", build_settings_context(request))


@require_POST
def settings_unlock_view(request):
    try:
        unlock_settings(
            request,
            profile_id=int(request.POST["profile_id"]),
            pin=request.POST.get("pin", ""),
        )
    except (KeyError, TypeError, ValueError, SettingsAuthError):
        return redirect(f"{reverse('settings')}?error=pin")
    return redirect("settings")


@require_POST
def settings_logout_view(request):
    logout_settings(request)
    return redirect("settings")


@require_POST
@settings_auth_required
def settings_member_create_view(request):
    name = request.POST.get("name", "").strip()
    pin = request.POST.get("pin", "")
    profile = Profile(
        name=name,
        avatar_url=request.POST.get("avatar_url", "").strip(),
        is_admin=request.POST.get("is_admin") == "on",
        pin_hash="",
    )
    try:
        profile.set_pin(pin)
        profile.save()
    except ValidationError:
        return redirect(f"{reverse('settings')}?error=member")
    return redirect("settings")


@require_POST
@settings_auth_required
def settings_member_update_view(request, member_id):
    profile = get_object_or_404(Profile, pk=member_id)
    profile.name = request.POST.get("name", profile.name).strip()
    profile.avatar_url = request.POST.get("avatar_url", "").strip()
    profile.is_admin = request.POST.get("is_admin") == "on"
    pin = request.POST.get("pin", "")
    if pin:
        try:
            profile.set_pin(pin)
        except ValidationError:
            return redirect(f"{reverse('settings')}?error=member")
    profile.save()
    return redirect("settings")


@require_POST
@settings_auth_required
def settings_perk_create_view(request):
    title = request.POST.get("title", "").strip()
    if not title:
        return redirect(f"{reverse('settings')}?error=perk")
    Perk.objects.create(
        title=title,
        description=request.POST.get("description", "").strip(),
        is_active=request.POST.get("is_active") == "on",
    )
    return redirect("settings")


@require_POST
@settings_auth_required
def settings_perk_toggle_view(request, perk_id):
    perk = get_object_or_404(Perk, pk=perk_id)
    perk.is_active = not perk.is_active
    perk.save(update_fields=["is_active"])
    return redirect("settings")


@require_POST
@settings_auth_required
def settings_template_create_view(request):
    title = request.POST.get("title", "").strip()
    if not title:
        return redirect(f"{reverse('settings')}?error=template")
    try:
        minutes = int(request.POST.get("estimated_minutes", 0))
    except (TypeError, ValueError):
        return redirect(f"{reverse('settings')}?error=template")
    ChoreTemplate.objects.create(
        title=title,
        category=request.POST.get("category", "").strip(),
        estimated_minutes=minutes,
        recurrence_rule=request.POST.get("recurrence_rule", "").strip(),
    )
    return redirect("settings")


@require_POST
@settings_auth_required
def settings_template_update_view(request, template_id):
    template = get_object_or_404(ChoreTemplate, pk=template_id)
    template.title = request.POST.get("title", template.title).strip()
    template.category = request.POST.get("category", template.category).strip()
    template.recurrence_rule = request.POST.get("recurrence_rule", template.recurrence_rule).strip()
    try:
        template.estimated_minutes = int(request.POST.get("estimated_minutes", template.estimated_minutes))
    except (TypeError, ValueError):
        return redirect(f"{reverse('settings')}?error=template")
    template.save()
    return redirect("settings")
