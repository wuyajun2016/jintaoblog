from django.conf.urls import url

from . import views

app_name = 'users'
urlpatterns = [
    url(r'^blog/register/$', views.register, name='register'),
    url(r'^blog/login/$', views.goLogin, name='goLogin'),
    url(r'^blog/user_login/$', views.user_login, name='user_login'),
    url(r'^blog/check_is_login/$', views.check_is_login, name='check_is_login'),
    url(r'^blog/user_logout/$', views.user_logout, name='user_logout'),
    url(r'^blog/goPasswordLost/$', views.goPasswordLost, name='goPasswordLost'),
    url(r'^blog/changepassword/$', views.changepassword, name='changepassword'),
    url(r'^user_active/([a-zA-Z]+)$',views.user_active,name='user_active'),
    url(r'^blog/get_email_code/$',views.get_email_code,name='get_email_code'),
    url(r'^blog/gousercenter/$',views.gousercenter,name='gousercenter'),
    url(r'^blog/gonickname_change/$',views.gonickname_change,name='gonickname_change'),
]