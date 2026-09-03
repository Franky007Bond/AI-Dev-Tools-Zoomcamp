from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from homework_quest.xp import xp_from_minutes


class Profile(models.Model):
    name = models.CharField(max_length=100)
    avatar_url = models.URLField(blank=True, default="")
    pin_hash = models.CharField(max_length=128)
    current_cycle_xp = models.PositiveIntegerField(default=0)
    total_wins = models.PositiveIntegerField(default=0)
    is_admin = models.BooleanField(default=False)

    def set_pin(self, pin: str) -> None:
        if len(pin) != 4 or not pin.isdigit():
            raise ValidationError("PIN must be exactly 4 digits.")
        self.pin_hash = make_password(pin)

    def check_pin(self, pin: str) -> bool:
        return check_password(pin, self.pin_hash)

    def __str__(self) -> str:
        return self.name


class ChoreTemplate(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    estimated_minutes = models.PositiveIntegerField()
    base_xp = models.PositiveIntegerField()
    recurrence_rule = models.CharField(max_length=200, blank=True, default="")

    def save(self, *args, **kwargs):
        self.base_xp = xp_from_minutes(self.estimated_minutes)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class ChoreStatus(models.TextChoices):
    OPEN = "Open", "Open"
    PENDING = "Pending", "Pending"
    APPROVED = "Approved", "Approved"


class ApprovalSource(models.TextChoices):
    PEER = "peer", "Peer"
    AUTO = "auto", "Auto"


class ChoreInstance(models.Model):
    template = models.ForeignKey(
        ChoreTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="instances",
    )
    title = models.CharField(max_length=200)
    xp_value = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=ChoreStatus.choices,
        default=ChoreStatus.OPEN,
    )
    assignee = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_chores",
    )
    approver = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_chores",
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    auto_approve_at = models.DateTimeField(null=True, blank=True)
    approved_via = models.CharField(
        max_length=10,
        choices=ApprovalSource.choices,
        blank=True,
        default="",
    )

    def mark_pending(self, submitted_at=None):
        if self.status == ChoreStatus.APPROVED:
            raise ValidationError("Approved chores cannot be submitted again.")
        submitted_at = submitted_at or timezone.now()
        self.status = ChoreStatus.PENDING
        self.submitted_at = submitted_at
        self.auto_approve_at = submitted_at + timedelta(hours=24)

    def approve(self, approver=None, via=ApprovalSource.PEER):
        if self.status != ChoreStatus.PENDING:
            raise ValidationError("Only pending chores can be approved.")
        self.status = ChoreStatus.APPROVED
        self.approver = approver
        self.approved_via = via

    def __str__(self) -> str:
        return self.title
