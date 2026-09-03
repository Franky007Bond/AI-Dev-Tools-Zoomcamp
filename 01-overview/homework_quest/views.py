import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from homework_quest.chore_pool import build_chore_pool_context
from homework_quest.dashboard import build_dashboard_context
from homework_quest.pin_overlay import build_pin_overlay_context
from homework_quest.review_queue import build_review_queue_context
from homework_quest.models import ChoreInstance, ChoreStatus, ChoreTemplate, Profile
from homework_quest.services import (
    ApprovalError,
    claim_open_bounty_for_profile,
    claim_open_bounty_with_pin,
    create_adhoc_bounty,
    log_chore,
    log_template_chore_for_profile,
    log_template_chore_with_pin,
    peer_approve,
)


def dashboard_view(request):
    return render(request, "homework_quest/dashboard.html", build_dashboard_context())


def chore_pool_view(request):
    tab = request.GET.get("tab", "routines")
    if tab not in {"routines", "bounties"}:
        tab = "routines"
    context = build_chore_pool_context(active_tab=tab)
    context.update(build_pin_overlay_context())
    return render(request, "homework_quest/chore_pool.html", context)


def review_pending_view(request):
    context = build_review_queue_context()
    context.update(build_pin_overlay_context())
    return render(
        request,
        "homework_quest/review_pending.html",
        context,
    )


@require_POST
def create_adhoc_bounty_view(request):
    try:
        create_adhoc_bounty(
            title=request.POST.get("title", ""),
            _category=request.POST.get("category", ""),
            estimated_minutes=int(request.POST.get("estimated_minutes", 0)),
        )
    except (ApprovalError, TypeError, ValueError):
        return redirect(f"{reverse('chore_pool')}?tab=bounties&error=1")
    return redirect(f"{reverse('chore_pool')}?tab=bounties")


@require_POST
def log_routine_view(request, template_id):
    try:
        template = ChoreTemplate.objects.get(pk=template_id)
        pin = request.POST.get("pin", "")
        profile_id = request.POST.get("profile_id")
        if profile_id:
            profile = Profile.objects.get(pk=profile_id)
            log_template_chore_for_profile(profile=profile, pin=pin, template=template)
        else:
            log_template_chore_with_pin(pin=pin, template=template)
    except (ChoreTemplate.DoesNotExist, Profile.DoesNotExist, ApprovalError):
        return redirect(f"{reverse('chore_pool')}?tab=routines&error=1")
    return redirect("dashboard")


@require_POST
def log_bounty_view(request, chore_id):
    try:
        chore = ChoreInstance.objects.get(pk=chore_id, status=ChoreStatus.OPEN)
        pin = request.POST.get("pin", "")
        profile_id = request.POST.get("profile_id")
        if profile_id:
            profile = Profile.objects.get(pk=profile_id)
            claim_open_bounty_for_profile(profile=profile, pin=pin, chore=chore)
        else:
            claim_open_bounty_with_pin(pin=pin, chore=chore)
    except (ChoreInstance.DoesNotExist, Profile.DoesNotExist, ApprovalError):
        return redirect(f"{reverse('chore_pool')}?tab=bounties&error=1")
    return redirect("dashboard")


def _parse_json(request):
    if not request.body:
        return {}
    return json.loads(request.body)


def _chore_payload(chore):
    return {
        "id": chore.pk,
        "title": chore.title,
        "status": chore.status,
        "xp_value": chore.xp_value,
        "approved_via": chore.approved_via,
        "assignee_id": chore.assignee_id,
        "approver_id": chore.approver_id,
    }


@csrf_exempt
@require_POST
def log_chore_view(request):
    try:
        data = _parse_json(request)
        assignee = Profile.objects.get(pk=data["profile_id"])
        chore = log_chore(
            assignee=assignee,
            pin=data["pin"],
            title=data["title"],
            xp_value=data["xp_value"],
        )
        return JsonResponse(_chore_payload(chore), status=201)
    except (KeyError, Profile.DoesNotExist, TypeError, ValueError):
        return JsonResponse({"error": "Invalid request."}, status=400)
    except ApprovalError as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@csrf_exempt
@require_POST
def approve_chore_view(request, chore_id):
    try:
        data = _parse_json(request)
        chore = ChoreInstance.objects.get(pk=chore_id)
        approver = Profile.objects.get(pk=data["approver_id"])
        peer_approve(chore=chore, approver=approver, pin=data["pin"])
        chore.refresh_from_db()
        return JsonResponse(_chore_payload(chore))
    except (KeyError, Profile.DoesNotExist, ChoreInstance.DoesNotExist, TypeError):
        return JsonResponse({"error": "Invalid request."}, status=400)
    except ApprovalError as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@csrf_exempt
@require_GET
def chore_detail_view(request, chore_id):
    try:
        chore = ChoreInstance.objects.get(pk=chore_id)
        return JsonResponse(_chore_payload(chore))
    except ChoreInstance.DoesNotExist:
        return JsonResponse({"error": "Chore not found."}, status=404)
