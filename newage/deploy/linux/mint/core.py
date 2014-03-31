# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import os

from fabric.api import run, settings
from fabric.contrib.files import append

from ..core import (Linux, SicrawebMixin, PyGmountMixin, RdesktopMixin,
                    BrowsersMixin, RdesktopDesktopManagerConf,
                    PygmountDesktopManagerConf)


class MintRdesktopDesktopManagerConf(RdesktopDesktopManagerConf):
    tss_url = ('http://openpa.zola.net/newage/deploy/$LOGNAME/tss/'
               '?format=url')

    def append_desktop_manager_conf(self):
        result = super(MintRdesktopDesktopManagerConf,
                       self).append_desktop_manager_conf()
        return result.format(tss_url=self.tss_url)


class Mint(SicrawebMixin, PyGmountMixin, RdesktopMixin, BrowsersMixin, Linux):

    home_skel = '/etc/skel'
    user_bash_profile = '.profile'
    sicraweb_data = {}
    list_desktop_manager_conf = [PygmountDesktopManagerConf,
                                 MintRdesktopDesktopManagerConf]

    def prepare_home_skel(self):
        sicraweb_launch_path = os.path.join(self.home_skel,
                                            self.sicraweb_launch_file)
        run("touch {}".format(sicraweb_launch_path))
        append(sicraweb_launch_path, self.sicraweb_launch_content)
        super(Mint, self).prepare_home_skel()

    def deploy_run(self):
        self.config_network()
        self.prepare_ssh_autologin()
        with settings(warn_only=True):
            self.update_apt_packages()
        self.prepare_python_env()
        self.prepare_rdesktop()
        self.prepare_sicraweb_jre(self.platform)
        self.prepare_ldap_client()
        self.prepare_home_skel()
        self.prepare_virtualenv_env()
        self.prepare_pygmount()
        self.prepare_browsers(self.platform)
        self.prepare_pygmount()
        self.prepare_desktop_manager_conf()


class Mint13(Mint):
    rdesktop_installers = {
        '32': 'http://ftp.de.debian.org/debian/pool/main/r/rdesktop/'
              'rdesktop_1.7.1-1_i386.deb',
        '64': 'http://ftp.de.debian.org/debian/pool/main/r/rdesktop/'
              'rdesktop_1.7.1-1_amd64.deb'}

    def deploy_root_tear_down(self):
        run('wget {}'.format(self.rdesktop_installers[self.platform]))
        run('dpkg -i {}'.format(
            self.rdesktop_installers[self.platform].split('/')[-1]))
        super(Mint13, self).deploy_tear_down()

    def config_network(self, *args, **kwargs):
        interface_file = '/etc/network/interfaces'
        run('mv {interface_file} {interface_file}.bak'.format(
            interface_file=interface_file))
        run('touch {}'.format(interface_file))
        append(interface_file, """auto lo
    iface lo inet loopback

    auto eth0
    iface eth0 inet dhcp""")
        run("/etc/init.d/networking restart")
        self.waiting_for(attempts=30)
        run('ifconfig')


class Mint16(Mint):
    def prepare_chrome(self, platform):
        run('apt-get install libcurl3')
        super(Mint16, self).prepare_chrome(platform)


class Ubuntu(SicrawebMixin, PyGmountMixin, RdesktopMixin, BrowsersMixin,
             Linux):
    home_skel = '/etc/skel'
    user_bash_profile = '.profile'
    sicraweb_data = {}
    list_desktop_manager_conf = [PygmountDesktopManagerConf,
                                 MintRdesktopDesktopManagerConf]

    def deploy_run(self):
        self.config_network()
        self.prepare_ssh_autologin()
        with settings(warn_only=True):
            self.update_apt_packages()
        self.prepare_python_env()


class Ubuntu1404(Ubuntu):
    pass
