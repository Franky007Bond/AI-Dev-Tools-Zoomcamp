"""
URL configuration for homework_quest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from homework_quest.ceremony_views import ceremony_view, start_new_cycle_view
from homework_quest.settings_views import (
    settings_logout_view,
    settings_member_create_view,
    settings_member_update_view,
    settings_perk_create_view,
    settings_perk_toggle_view,
    settings_template_create_view,
    settings_template_update_view,
    settings_unlock_view,
    settings_view,
)
from homework_quest.views import (
    chore_pool_view,
    create_adhoc_bounty_view,
    dashboard_view,
    log_bounty_view,
    log_routine_view,
    review_pending_view,
)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('dashboard/', dashboard_view, name='dashboard-alt'),
    path('chore-pool/', chore_pool_view, name='chore_pool'),
    path('chore-pool/bounty/', create_adhoc_bounty_view, name='create_adhoc_bounty'),
    path(
        'chore-pool/log-routine/<int:template_id>/',
        log_routine_view,
        name='log_routine',
    ),
    path('chore-pool/log-bounty/<int:chore_id>/', log_bounty_view, name='log_bounty'),
    path('review-pending/', review_pending_view, name='review_pending'),
    path('ceremony/', ceremony_view, name='ceremony'),
    path('ceremony/start/', start_new_cycle_view, name='start_new_cycle'),
    path('settings/', settings_view, name='settings'),
    path('settings/unlock/', settings_unlock_view, name='settings_unlock'),
    path('settings/logout/', settings_logout_view, name='settings_logout'),
    path('settings/members/', settings_member_create_view, name='settings_member_create'),
    path(
        'settings/members/<int:member_id>/',
        settings_member_update_view,
        name='settings_member_update',
    ),
    path('settings/perks/', settings_perk_create_view, name='settings_perk_create'),
    path(
        'settings/perks/<int:perk_id>/toggle/',
        settings_perk_toggle_view,
        name='settings_perk_toggle',
    ),
    path(
        'settings/templates/',
        settings_template_create_view,
        name='settings_template_create',
    ),
    path(
        'settings/templates/<int:template_id>/',
        settings_template_update_view,
        name='settings_template_update',
    ),
    path('admin/', admin.site.urls),
    path('api/', include('homework_quest.api_urls')),
]
