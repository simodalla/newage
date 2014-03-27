# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView
from django.utils.translation import ugettext_lazy as _

from .models import RdesktopSession, RdesktopUser


class DeployRdesktopTerminalServerList(ListView):

    content_type = 'text/plain'
    http_method_names = ['get']
    template_name = 'newage/deploy/terminalserver_list.txt'

    def render_to_response(self, context, **response_kwargs):
        response = super(DeployRdesktopTerminalServerList,
                         self).render_to_response(context, **response_kwargs)
        response['Content-Disposition'] = (
            'attachment; filename="terminal_servers.txt"')
        return response

    def get_queryset(self):
        user = get_object_or_404(RdesktopUser,
                                 username__iexact=self.kwargs['username'])
        return RdesktopSession.objects.filter(user=user).order_by(
            'server__fqdn')


class DeployRdesktopSessionDetail(DetailView):

    model = RdesktopSession
    content_type = 'text/plain'
    http_method_names = ['get']
    template_name = 'newage/deploy/rdesktopsession_detail.txt'

    def render_to_response(self, context, **response_kwargs):
        response = super(DeployRdesktopSessionDetail,
                         self).render_to_response(context, **response_kwargs)
        response['Content-Disposition'] = (
            'attachment; filename="redsktop_{}.desktop"'.format(
                self.kwargs.get('fqdn')))
        return response

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        username = self.kwargs.get('username')
        fqdn = self.kwargs.get('fqdn')
        try:
            obj = queryset.filter(
                user__username__iexact=username,
                server__fqdn__iexact=fqdn).get()
        except ObjectDoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj
