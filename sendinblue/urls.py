from django.conf.urls import url

from .views import dashboard

urlpatterns = [
    url(r'^dashboard/$', dashboard, name='dashboard'),
]
