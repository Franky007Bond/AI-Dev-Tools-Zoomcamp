import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from homework_quest.dashboard import build_dashboard_context
from homework_quest.models import ChoreInstance, Profile
from homework_quest.services import ApprovalError, log_chore, peer_approve


def dashboard_view(request):
    return render(request, "homework_quest/dashboard.html", build_dashboard_context())


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
