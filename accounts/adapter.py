from allauth.account.adapter import DefaultAccountAdapter


class NoSignupAdapter(DefaultAccountAdapter):
    """Bloqueia self-signup público. Contas são criadas via admin ou via
    formulários internos (Aluno/Professor) por usuários autorizados."""

    def is_open_for_signup(self, request):
        return False
