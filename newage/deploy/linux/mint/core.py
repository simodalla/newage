# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import os

from fabric.api import run
from fabric.contrib.files import append, sed

from ..core import (Linux, SicrawebMixin, PyGmountMixin, RdesktopMixin,
                    BrowsersMixin)


class Mint(SicrawebMixin, PyGmountMixin, RdesktopMixin, BrowsersMixin, Linux):

    home_skel = '/etc/skel'
    user_bash_profile = '.profile'
    sicraweb_data = {}

    def prepare_home_skel(self):
        sicraweb_launch_path = os.path.join(self.home_skel,
                                            self.sicraweb_launch_file)
        run("touch {}".format(sicraweb_launch_path))
        append(sicraweb_launch_path, self.sicraweb_launch_content)
        super(Mint, self).prepare_home_skel()

    def deploy_run(self):
        self.config_network()
        self.prepare_ssh_autologin()
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


class Mint13(Mint):
    rdesktop_installers = {
        '32': 'http://ftp.de.debian.org/debian/pool/main/r/rdesktop/'
              'rdesktop_1.7.1-1_i386.deb',
        '64': 'http://ftp.de.debian.org/debian/pool/main/r/rdesktop/'
              'rdesktop_1.7.1-1_amd64.deb'}

    def deploy_tear_down(self):
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
