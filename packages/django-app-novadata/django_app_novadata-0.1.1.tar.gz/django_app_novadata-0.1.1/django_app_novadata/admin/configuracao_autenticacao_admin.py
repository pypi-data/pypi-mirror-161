from django.contrib import admin

from ..models import ConfiguracaoAutenticacao


@admin.register(ConfiguracaoAutenticacao)
class ConfiguracaoAutenticacaoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
    ]

    search_fields = [
        'id',
    ]

    class Media:

        js = (
            'django_app_novadata/js/admin_configuracao_autenticacao.js',  # app static folder
        )