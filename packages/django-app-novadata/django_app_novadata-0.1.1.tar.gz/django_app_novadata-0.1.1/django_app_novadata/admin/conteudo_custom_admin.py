from django.contrib import admin

from ..models import ConteudoCustom


@admin.register(ConteudoCustom)
class ConteudoCustomAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'local',
    ]

    search_fields = [
        'id',
        'local',
    ]

    list_filter = [
        'local',
    ]

    class Media:

        js = (
            'django_app_novadata/js/admin_conteudo_custom.js',  # app static folder
        )