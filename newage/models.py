# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel


@python_2_unicode_compatible
class SambaDomain(TimeStampedModel):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name = _('Samba Domain')
        verbose_name_plural = _('Samba Domains')
        ordering = ('name',)

    def __str__(self):
        return self.name


class BaseHost(TimeStampedModel):
    hostname = models.CharField(max_length=50, unique=True)
    fqdn = models.CharField(max_length=50, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    samba_domain = models.ForeignKey(SambaDomain, blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.hostname = self.hostname.lower()
        self.fqdn = self.fqdn.lower()
        super(BaseHost, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Printer(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Server(BaseHost):

    class Meta:
        verbose_name = _('Server')
        verbose_name_plural = _('Server')
        ordering = ('fqdn',)

    def __str__(self):
        return self.fqdn


@python_2_unicode_compatible
class TerminalServer(Server):

    class Meta:
        verbose_name = _('Terminal Server')
        verbose_name_plural = _('Terminal Server')

    def __str__(self):
        return self.fqdn


@python_2_unicode_compatible
class RdesktopUser(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    username = models.CharField(max_length=30, unique=True)

    class Meta:
        verbose_name = _('Rdesktop User')
        verbose_name_plural = _('Rdesktop User')
        ordering = ('username',)

    def __str__(self):
        return self.username


@python_2_unicode_compatible
class RdesktopSession(TimeStampedModel):
    user = models.ForeignKey(RdesktopUser)
    server = models.ForeignKey(TerminalServer)
    fullscreen = models.BooleanField(default=False)
    geometry_width = models.PositiveIntegerField(blank=True, null=True)
    geometry_height = models.PositiveIntegerField(blank=True, null=True)
    printer_queues_raw = models.TextField(blank=True)
    smartcard_raw = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Rdesktop Session')
        verbose_name_plural = _('Rdesktop Session')
        ordering = ('user__username',)
        unique_together = ('user', 'server',)

    def __str__(self):
        return '{}--{}'.format(self.user, self.server)

    @property
    def geometry(self):
        if self.geometry_width and self.geometry_height:
            return '{}x{}'.format(self.geometry_width, self.geometry_height)
        return ''

    @property
    def command(self):
        result = 'rdesktop -P'
        if self.server.samba_domain:
            result += ' -d {}'.format(self.server.samba_domain)
        if self.fullscreen:
            result += ' -f'
        elif self.geometry:
            result += ' -g {}'.format(self.geometry)
        elif self.printer_queues_raw:
            result += ' {}'.format(self.printer_queues_raw.strip(' '))
        result += ' -r scard'

        return '{} {}'.format(result, self.server.fqdn)

    def get_absolute_url(self):
        return reverse('newage:deploy_rdesktop_session_detail',
                       kwargs={'username': self.user.username,
                               'fqdn': self.server.fqdn})
