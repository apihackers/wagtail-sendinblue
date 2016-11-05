from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from .views import submit_form

urlpatterns = [
    url(r'^sib/form/(?P<pk>\d+)$', submit_form, name='sendinblue-form'),
]
