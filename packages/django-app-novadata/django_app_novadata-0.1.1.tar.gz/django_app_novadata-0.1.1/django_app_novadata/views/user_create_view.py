from django.contrib.auth.forms import UserCreationForm
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from ..models import ConfiguracaoAutenticacao

class UserCreateView(CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        configuracao_geral = ConfiguracaoAutenticacao.objects.filter(local='Geral - Site').last()
        if not configuracao_geral.possui_cadastro:
            raise Http404()

        context['config_site'] = ConfiguracaoAutenticacao.objects.filter(local='Register - Site').last()

        return context

    form_class = UserCreationForm
    success_url = reverse_lazy('login_site')
    template_name = 'login_site/register.html'