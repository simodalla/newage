# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import admin

from .models import SambaDomain, TerminalServer, RdesktopUser, RdesktopSession


class RdesktopSessionInline(admin.TabularInline):
    extra = 3
    model = RdesktopSession
    ordering = ['server__fqdn']


class SambaDomainAdmin(admin.ModelAdmin):
    list_display = ['name']


class TerminalServerAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'fqdn', 'ip_address', 'samba_domain']
    list_editable = ['fqdn', 'ip_address', 'samba_domain']
    list_per_page = 20


class RdesktopUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'username']
    list_editable = ['username']
    inlines = [RdesktopSessionInline]


class RdesktopSessionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'server', 'fullscreen', 'geometry',
                    'printer_queues_raw', 'smartcard_raw']
    list_editable = ['user', 'server', 'fullscreen']
    list_per_page = 20
    list_filter = ['user', 'server']


admin.site.register(SambaDomain, SambaDomainAdmin)
admin.site.register(TerminalServer, TerminalServerAdmin)
admin.site.register(RdesktopUser, RdesktopUserAdmin)
admin.site.register(RdesktopSession, RdesktopSessionAdmin)
