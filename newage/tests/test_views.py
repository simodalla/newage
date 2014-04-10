# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
User = get_user_model()

from ..models import RdesktopUser, TerminalServer, SambaDomain


class DeployRdesktopTerminalServerListTest(TestCase):

    def setUp(self):
        user = User.objects.create_user('user_1', 'user_1@example.com',
                                        'defualt')
        self.rdesktop_user = RdesktopUser.objects.create(
            user=user, username=user.username)
        dns_domain = '.local'
        samba_domain = SambaDomain.objects.create(name='SAMBADOMAIN')
        for i in xrange(0, 3):
            ts = TerminalServer.objects.create(
                hostname='ts_server_{}'.format(i),
                fqdn='ts_server_{}{}'.format(i, dns_domain),
                samba_domain=samba_domain)
            self.rdesktop_user.rdesktopsession_set.create(server=ts)

    def test_call_view_with_wrong_user(self):
        response = self.client.get(
            reverse('newage:deploy_terminalservers_list',
                    kwargs={'username': 'fake_user'}))
        self.assertEqual(response.status_code, 404)

    def test_call_view_response_content_type_is_text_plain(self):
        response = self.client.get(
            reverse('newage:deploy_terminalservers_list',
                    kwargs={'username': self.rdesktop_user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')

    def test_call_view_response_has_content_disposition_header(self):
        response = self.client.get(
            reverse('newage:deploy_terminalservers_list',
                    kwargs={'username': self.rdesktop_user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="terminal_servers.txt"')

    def test_call_view_response_content(self):
        response = self.client.get(
            reverse('newage:deploy_terminalservers_list',
                    kwargs={'username': self.rdesktop_user.username}))
        self.assertEqual(response.status_code, 200)
        print(response.content)
        expected_content = '\n'.join(
            [str(session.server.fqdn) for session in
             self.rdesktop_user.rdesktopsession_set.order_by('server__fqdn')])
        self.assertEqual(response.content.rstrip('\n').lstrip('\n'),
                         expected_content)


class DeployRdesktopSessionDetailTest(TestCase):
    def setUp(self):
        user = User.objects.create_user('user_1', 'user_1@example.com',
                                        'defualt')
        self.rdesktop_user = RdesktopUser.objects.create(
            user=user, username=user.username)
        dns_domain = '.local'
        samba_domain = SambaDomain.objects.create(name='SAMBADOMAIN')
        for i in xrange(0, 3):
            ts = TerminalServer.objects.create(
                hostname='ts_server_{}'.format(i),
                fqdn='ts_server_{}{}'.format(i, dns_domain),
                samba_domain=samba_domain)
            self.rdesktop_user.rdesktopsession_set.create(server=ts)

    def test_call_view_response_content_type_is_text_plain(self):
        session = self.rdesktop_user.rdesktopsession_set.all()[0]
        print(session.server.fqdn)
        response = self.client.get(
            reverse('newage:deploy_rdesktop_session_detail',
                    kwargs={'username': self.rdesktop_user.username,
                            'fqdn': session.server.fqdn}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')

    def test_call_view_response_has_content_disposition_header(self):
        session = self.rdesktop_user.rdesktopsession_set.all()[0]
        response = self.client.get(
            reverse('newage:deploy_rdesktop_session_detail',
                    kwargs={'username': self.rdesktop_user.username,
                            'fqdn': session.server.fqdn}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="redsktop_{server.fqdn}'
                         '.desktop"'.format(server=session.server))

    def test_call_view_response_content(self):
        session = self.rdesktop_user.rdesktopsession_set.all()[0]
        response = self.client.get(
            reverse('newage:deploy_rdesktop_session_detail',
                    kwargs={'username': self.rdesktop_user.username,
                            'fqdn': session.server.fqdn}))
        self.assertEqual(response.status_code, 200)
