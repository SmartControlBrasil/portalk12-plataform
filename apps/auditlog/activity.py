from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from django.utils import timezone

from apps.auditlog.services import get_client_ip, get_user_agent


def mark_user_activity(user: Any, request: HttpRequest | None = None) -> None:
    """
    Marca atividade recente do usuário.

    Regra:
    - não registra usuário anônimo;
    - atualiza o perfil se os campos existirem;
    - evita salvar em toda requisição quando a última atividade foi há poucos minutos.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return

    profile = getattr(user, "profile", None)

    if not profile or not hasattr(profile, "last_activity_at"):
        return

    now = timezone.now()
    last_activity_at = getattr(profile, "last_activity_at", None)

    # Evita escrita excessiva no banco em navegação intensa.
    if last_activity_at and (now - last_activity_at).total_seconds() < 300:
        return

    update_fields = ["last_activity_at"]

    profile.last_activity_at = now

    if request is not None and hasattr(profile, "last_activity_ip"):
        profile.last_activity_ip = get_client_ip(request)
        update_fields.append("last_activity_ip")

    if request is not None and hasattr(profile, "last_activity_user_agent"):
        profile.last_activity_user_agent = get_user_agent(request)
        update_fields.append("last_activity_user_agent")

    profile.save(update_fields=update_fields)
