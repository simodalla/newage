# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import os

from fabric.api import run, settings, abort
from fabric.colors import red
from fabric.contrib.files import append

from ..core import (Linux, SicrawebMixin, PyGmountMixin, RdesktopMixin,
                    BrowsersMixin, MateMixin, PamMountMixin, SmartCardMixin)


class Mint(PamMountMixin, SicrawebMixin, MateMixin, RdesktopMixin,
           SmartCardMixin, BrowsersMixin, Linux):

    home_skel = '/etc/skel'
    user_bash_profile = '.profile'
    sicraweb_data = {}

    def prepare_home_skel(self):
        sicraweb_launch_path = os.path.join(self.home_skel,
                                            self.sicraweb_launch_file)
        run("touch {}".format(sicraweb_launch_path))
        append(sicraweb_launch_path, self.sicraweb_launch_content)
        super(Mint, self).prepare_home_skel()

    def deploy_set_up(self):
        check, errors = self.mate_check_config_files()
        if not check:
            abort(red(errors))
        super(Mint, self).deploy_set_up()

    def deploy_run(self):
        self.prepare_ssh_autologin()
        with settings(warn_only=True):
            self.update_apt_packages()
        self.prepare_python_env()
        self.prepare_smartcard(self.platform)
        self.prepare_rdesktop()
        self.prepare_sicraweb_jre(self.platform)
        self.prepare_ldap_client()
        self.prepare_virtualenv_env()
        self.prepare_browsers(self.platform)
        self.prepare_mate_env()
        self.prepare_pam_mount()
        self.prepare_home_skel()


class Mint13(Mint):
    rdesktop_installers = {
        '32': 'http://ftp.de.debian.org/debian/pool/main/r/rdesktop/'
              'rdesktop_1.7.1-1_i386.deb',
        '64': 'http://ftp.de.debian.org/debian/pool/main/r/rdesktop/'
              'rdesktop_1.7.1-1_amd64.deb'}

    def deploy_root_tear_down(self):
        run('apt-get install -y smbfs')
        run('wget {}'.format(self.rdesktop_installers[self.platform]))
        run('dpkg -i {}'.format(
            self.rdesktop_installers[self.platform].split('/')[-1]))
        super(Mint13, self).deploy_tear_down()


class Mint16(Mint):

    def prepare_chrome(self, platform):
        run('apt-get install libcurl3')
        super(Mint16, self).prepare_chrome(platform)


class Ubuntu(SicrawebMixin, PyGmountMixin, RdesktopMixin, BrowsersMixin,
             Linux):
    home_skel = '/etc/skel'
    user_bash_profile = '.profile'
    sicraweb_data = {}

    def deploy_run(self):
        self.config_network()
        self.prepare_ssh_autologin()
        with settings(warn_only=True):
            self.update_apt_packages()
        self.prepare_python_env()


class Ubuntu1404(Ubuntu):
    pass
