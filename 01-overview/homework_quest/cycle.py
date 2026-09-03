"""Weekly cycle winner selection for Homework Quest."""


def select_winners(xp_by_profile_id: dict[int, int]) -> list[int]:
    """Return the unique top scorer, or every profile tied for first place."""
    if not xp_by_profile_id:
        return []
    top_xp = max(xp_by_profile_id.values())
    return [profile_id for profile_id, xp in xp_by_profile_id.items() if xp == top_xp]
