import pytest

from homework_quest.models import Profile


@pytest.mark.django_db
def test_new_profile_starts_with_zero_xp_and_wins():
    profile = Profile.objects.create(name="Alex", pin_hash="unused")

    assert profile.current_cycle_xp == 0
    assert profile.total_wins == 0


@pytest.mark.django_db
def test_set_pin_stores_hash_not_plaintext():
    profile = Profile(name="Alex", pin_hash="")
    profile.set_pin("1234")
    profile.save()

    assert profile.pin_hash != "1234"
    assert profile.check_pin("1234") is True


@pytest.mark.django_db
def test_check_pin_rejects_wrong_pin():
    profile = Profile(name="Alex", pin_hash="")
    profile.set_pin("1234")
    profile.save()

    assert profile.check_pin("5678") is False
