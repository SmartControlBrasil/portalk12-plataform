from __future__ import annotations

from typing import Any

from django.utils import timezone


def mark_user_activity(user: Any) -> None:
    """
    Marca atividade recente do usuário.

    Por enquanto este método é intencionalmente leve.
    Futuramente poderá atualizar campos como:
    - last_activity_at
    - last_seen_at
    - last_activity_ip
    - last_activity_user_agent
    """
    if not user or not getattr(user, "is_authenticated", False):
        return

    profile = getattr(user, "profile", None)

    if profile and hasattr(profile, "last_activity_at"):
        profile.last_activity_at = timezone.now()
        profile.save(update_fields=["last_activity_at"])
