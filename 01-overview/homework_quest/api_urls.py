from django.urls import path

from homework_quest import views

urlpatterns = [
    path("dashboard/", views.dashboard_json_view, name="dashboard_json"),
    path("chores/log/", views.log_chore_view, name="log_chore"),
    path("chores/<int:chore_id>/approve/", views.approve_chore_view, name="approve_chore"),
    path("chores/<int:chore_id>/", views.chore_detail_view, name="chore_detail"),
]
