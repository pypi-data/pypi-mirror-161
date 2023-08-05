from django.apps import AppConfig

class DjangoAppNovadataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_app_novadata'

    def ready(self):
        import django_app_novadata.signals
