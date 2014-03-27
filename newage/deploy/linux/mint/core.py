# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import os

from fabric.api import run
from fabric.contrib.files import append, sed

from linux.core import Linux, SicrawebMixin, PyGmountMixin


class Mint(SicrawebMixin, PyGmountMixin, Linux):

    home_skel = '/etc/skel'
    user_bash_profile = '.profile'
    sicraweb_data = {}

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

    def prepare_home_skel(self):
        sicraweb_launch_path = os.path.join(self.home_skel,
                                            self.sicraweb_launch_file)
        run("touch {}".format(sicraweb_launch_path))
        append(sicraweb_launch_path, self.sicraweb_launch_content)

        for key, old_value, new_value in [
                ('browser.startup.homepage',
                 'http://www.linuxmint.com/start/maya',
                 'http://pympa.zola.net/'),
                ('browser.search.selectedEngine', 'Yahoo', 'Google'),
                ('browser.search.order.1', 'Yahoo', 'Google')]:
            sed('{}/.mozilla/firefox/mwad0hks.default/prefs.js'.format(
                self.home_skel),
                'user_pref\(\\"{}\\", \\"{}\\"\);'.format(key, old_value),
                'user_pref("{}", "{}");'.format(key, new_value))

    def prepare_virtualenv_env(self):
        run('pip install -U virtualenv virtualenvwrapper')
        append(self.user_bash_profile, """export WORKON_HOME=/opt/virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
export PIP_VIRTUALENV_BASE=$WORKON_HOME
export PIP_DOWNLOAD_CACHE=$HOME/.pip-cache""")



class Mint13(Mint):
    pass
