from django.urls import path
from django_app_novadata.views.login_site_view import LoginSiteView
from django_app_novadata.views.logout_site_view import LogoutSiteView
from django_app_novadata.views.password_change_done_site_view import PasswordChangeDoneSiteView
from django_app_novadata.views.password_change_site_view import PasswordChangeSiteView
from django_app_novadata.views.password_reset_complete_site_view import PasswordResetCompleteSiteView
from django_app_novadata.views.password_reset_confirm_site_view import PasswordResetConfirmSiteView
from django_app_novadata.views.password_reset_done_site_view import PasswordResetDoneSiteView
from django_app_novadata.views.password_reset_site_view import PasswordResetSiteView
from django_app_novadata.views.user_create_view import UserCreateView

urlpatterns = [
    path('login/', LoginSiteView.as_view(template_name="login_site/login.html"), name='login_site'),

    path('logout/', LogoutSiteView.as_view(template_name="login_site/logout.html"), name='encerrar_sessao'),

    path('password_change/', PasswordChangeSiteView.as_view(template_name="login_site/password_change_form.html"), name='password_change'),
    
    path('password_change/done/', PasswordChangeDoneSiteView.as_view(template_name="login_site/password_change_done.html"), name='password_change_done'),

    path('password_reset/', PasswordResetSiteView.as_view(template_name="login_site/password_reset_form.html"), name='password_reset'),

    path('password_reset/done/', PasswordResetDoneSiteView.as_view(template_name="login_site/password_reset_done.html"), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', PasswordResetConfirmSiteView.as_view(template_name="login_site/password_reset_confirm.html"), name='password_reset_confirm'),

    path('reset/done/', PasswordResetCompleteSiteView.as_view(template_name="login_site/password_resete_complete.html"), name='password_reset_complete'),

    path('register/', UserCreateView.as_view(), name='register'),
]
