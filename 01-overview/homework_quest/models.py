from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.db import models


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
