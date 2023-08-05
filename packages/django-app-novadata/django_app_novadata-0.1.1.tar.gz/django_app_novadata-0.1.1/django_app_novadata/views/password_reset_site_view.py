from django.contrib.auth.views import PasswordResetView
from django.http import Http404
from ..models import ConfiguracaoAutenticacao

class PasswordResetSiteView(PasswordResetView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        configuracao_geral = ConfiguracaoAutenticacao.objects.filter(local='Geral - Site').last()
        if not configuracao_geral.possui_troca_senha:
            raise Http404()

        context['config_site'] = ConfiguracaoAutenticacao.objects.filter(local='Password Reset Form - Site').last()

        return context