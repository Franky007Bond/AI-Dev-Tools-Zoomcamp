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

from homework_quest.views import (
    chore_pool_view,
    create_adhoc_bounty_view,
    dashboard_view,
    log_bounty_view,
    log_routine_view,
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
    path('admin/', admin.site.urls),
    path('api/', include('homework_quest.api_urls')),
]
