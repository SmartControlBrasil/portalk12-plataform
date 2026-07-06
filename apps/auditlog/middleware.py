from __future__ import annotations

from apps.auditlog.activity import mark_user_activity


class UserActivityMiddleware:
    """
    Atualiza última atividade de usuários autenticados.

    Este middleware não cria AuditLog para cada requisição.
    Ele apenas mantém last_activity_at/IP/user-agent no perfil,
    com throttling interno para não gravar no banco a cada clique.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            mark_user_activity(request.user, request=request)
        except Exception:
            # Atividade não pode derrubar navegação do usuário.
            # Futuramente podemos registrar erro técnico em observabilidade.
            pass

        return response
