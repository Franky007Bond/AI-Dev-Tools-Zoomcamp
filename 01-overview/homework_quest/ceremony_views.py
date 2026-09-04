from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from homework_quest.ceremony import build_ceremony_context
from homework_quest.cycle import CycleError, close_weekly_cycle


def ceremony_view(request):
    celebrating = request.GET.get("reset") == "1"
    error = request.GET.get("error") == "1"
    return render(
        request,
        "homework_quest/ceremony.html",
        {
            **build_ceremony_context(celebrating=celebrating),
            "reset_error": error,
        },
    )


@require_POST
def start_new_cycle_view(request):
    try:
        close_weekly_cycle()
    except CycleError:
        return redirect(f"{reverse('ceremony')}?error=1")
    return redirect(f"{reverse('ceremony')}?reset=1")
