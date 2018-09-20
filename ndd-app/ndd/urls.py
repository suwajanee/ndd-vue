"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django.views.generic import RedirectView

from booking.views.authentication_view import AuthenticationView
from booking.views.response_server import error_404, error_500
from booking.views.export_xls_view import ExportDataView


urlpatterns = [
    path('ndd-admin/', admin.site.urls),
    path('booking/', include('booking.urls')),
    path('agent-transport/', include('agent_transport.urls')),
    path('customer/', include('customer.urls')),

    url(r'^staff/$', AuthenticationView.login, name='login'),
    url(r'^logout/$', AuthenticationView.logout, name='logout'),

    url(r'^$', RedirectView.as_view(url='/staff/')),

    url(r'^export/$', ExportDataView.render_export_page, name='export-page'),
    url(r'^export/work/$', ExportDataView.export_xls, name='export-work'),

]

handler404 = error_404
handler500 = error_500


