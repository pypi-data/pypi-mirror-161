from django.db import models


class ConfiguracaoAutenticacao(models.Model):
    '''
    A classe ConfiguracaoLoginSite serve para armazernar os(as) configuracao do sistema.
    Além de fazer as implementações relacionadas a um único objeto do tipo ConfiguracaoLoginSite.
    '''

    LOCAL_CHOICES = (
        ('Nenhum Local','Nenhum Local'),
        ('Login - Site','Login - Site'),
        ('Logout - Site', 'Logout - Site'),
        ('Register - Site','Register - Site'),
        ('Password Change Done - Site','Password Change Done - Site'),
        ('Password Change Form - Site','Password Change Form - Site'),
        ('Password Reset Complete - Site','Password Reset Complete - Site'),
        ('Password Reset Done - Site','Password Reset Done - Site'),
        ('Password Reset Email - Site','Password Reset Email - Site'),
        ('Password Reset Form - Site','Password Reset Form - Site'),
        ('Geral - Site','Geral - Site')
    )

    local = models.CharField(
        verbose_name='Página',
        max_length=100,
        choices=LOCAL_CHOICES,
        default='Nenhum Local',
        help_text="Apenas o último cadastrado será valido!"
    )

    titulo = models.CharField(
        verbose_name='titulo',
        max_length=100,
        blank=True,
        null=True
    )

    logo = models.FileField(
        verbose_name="Logo",
        upload_to="login_site/logo/",
        null=True,
        blank=True
    )

    possui_troca_senha = models.BooleanField(
        verbose_name="Possui Troca de Senha?",
        default=False,
        blank=True
    )

    possui_cadastro = models.BooleanField(
        verbose_name="Possui Cadastro?",
        default=False,
        blank=True
    )

    extra_head = models.TextField(
        verbose_name="Head Extra",
        null=True,
        blank=True
    )

    extra_style = models.TextField(
        verbose_name="Style Extra",
        null=True,
        blank=True
    )

    extra_js = models.TextField(
        verbose_name="Js Extra",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.local

    class Meta:
        app_label = 'django_app_novadata'
        verbose_name = 'Configuração - Autenticação'
        verbose_name_plural = 'Configuração - Autenticação'
