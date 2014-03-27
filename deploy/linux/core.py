# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import os.path
import time

from fabric.api import abort, run, prefix, warn_only, cd
from fabric.contrib.files import exists, append, contains
from fabric.colors import yellow, red
from fabric.exceptions import NetworkError


class Linux(object):

    home_skel = '/etc/skel'
    user_bash_profile = '.profile'

    def __init__(self, platform=32):
        self.platform = str(platform)

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, platform):
        self.check_platform(platform)
        self._platform = str(platform)

    @staticmethod
    def check_platform(platform):
        platforms = ['32', '64']
        if platform not in platforms:
            abort('platform selectables are [{platforms}]'.format(
                platforms='/'.join(platforms)))

    @staticmethod
    def waiting_for(attempts=9, interval=1):
        for attempt in range(0, attempts):
            try:
                run('ls', quiet=True)
            except NetworkError:
                print(yellow("attempt n: {}".format(attempt)))
                time.sleep(interval)
                continue
            break

    def config_network(self, *args, **kwargs):
        pass

    def prepare_home_skel(self):
        pass


class SicrawebMixin(object):

    sicraweb_launch_file = 'command.properties'
    sicraweb_launch_content = 'COMMAND=gnome-open '

    def get_sicraweb_launch_file(self, *args, **kwargs):
        return self.sicraweb_launch_file

    def get_sicraweb_launch_content(self, *args, **kwargs):
        return self.sicraweb_launch_content


class PyGmountMixin(object):

    pyzenity_installer = ('http://openpa.zola.net/static_open_pa/media/uploa'
                          'ds/site-4/software/pylogon/PyZenity-0.1.7.tar.gz')
    pygmount_rc_skel = ('http://openpa.zola.net/static_open_pa/media/uploads/'
                        'site-4/software/pylogon/pygmount_skel.rc')
    virtualenv_name = 'pygmount'
    sudoers_path = '/etc/sudoers.d/mounters_sudoers'
    mount_command_name = 'mount-smb-shares'

    @property
    def mount_command_system_path(self):
        return os.path.join('/usr/bin', self.mount_command_name)

    @property
    def mount_command_venv_path(self):
        workon_home = run('echo $WORKON_HOME')
        if not workon_home:
            abort(red('$WORKON_HOME is not set, check virtualenv into system'
                      ' or files .profile/.bash_rc/.bash_profile'))
        return os.path.join(workon_home, self.virtualenv_name,
                            'bin', self.mount_command_name)

    def prepare_pygmount(self):
        with warn_only():
            result = run('workon {}'.format(self.virtualenv_name))
        if result.failed:
            run('mkvirtualenv --system-site-packages {}'.format(
                self.virtualenv_name))

        with prefix('workon {}'.format(self.virtualenv_name)):
            run('pip install {}'.format(self.pyzenity_installer))
            run('pip install PyGmount')

        if not exists(self.sudoers_path):
            run('touch {}'.format(self.sudoers_path))
        run('update-alternatives --install "{}" "{}"'
            ' "{}" 1'.format(self.mount_command_system_path,
                             self.mount_command_name,
                             self.mount_command_venv_path))
        append(self.sudoers_path,
               "%mounters ALL=(ALL) /sbin/mount.cifs, /bin/umount,"
               " {}".format(self.mount_command_system_path))
        run('chmod 440 {}'.format(self.sudoers_path))
        run('wget -O /etc/skel/.pygmount.rc {}'.format(self.pygmount_rc_skel))

        with cd('/etc/mdm/PostLogin/'):
            if not exists('Default'):
                run('cp Default.sample Default')
            if not contains('Default', '.pygmount.rc'):
                append(
                    'Default',
                    'sed -i -e "s/\\\$USER/${LOGNAME}/g" $HOME/.pygmount.rc',
                    partial=True)


