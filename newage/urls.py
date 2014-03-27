# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import patterns, url

from .views import (DeployRdesktopTerminalServerList,
                    DeployRdesktopSessionDetail)


urlpatterns = patterns(
    'newage.views',
    url(r'^deploy/(?P<username>[_\w]+)/tss/$',
        DeployRdesktopTerminalServerList.as_view(),
        name='deploy_terminalservers_list'),
    url(r'^deploy/(?P<username>[_\w]+)/rdesktop/(?P<fqdn>[\w.]*\w+)/$',
        DeployRdesktopSessionDetail.as_view(),
        name='deploy_rdesktop_session_detail'),
)
