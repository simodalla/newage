# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import os
import os.path
from getpass import getpass
import time

from fabric.api import abort, run, prefix, warn_only, cd, settings, sudo, put
from fabric.contrib.files import exists, append, contains, sed
from fabric.colors import yellow, red, green, magenta
from fabric.exceptions import NetworkError


class Linux(object):

    home_skel = '/etc/skel'
    user_bash_profile = '.profile'
    get_pip_file = 'https://raw.github.com/pypa/pip/master/contrib/get-pip.py'
    ldap_client_conf_path = None
    list_desktop_manager_conf = []

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

    def deploy_set_up(self):
        self.prepare_ssh_autologin()
        sudo("passwd root")

    def deploy_tear_down(self):
        sudo("passwd -dl root")

    def deploy_root_set_up(self):
        pass

    def deploy_run(self):
        pass

    def deploy_root_tear_down(self):
        pass

    def deploy(self):
        self.deploy_set_up()
        with settings(user='root'):
            self.deploy_root_set_up()
            self.deploy_run()
            self.deploy_root_tear_down()
        self.deploy_tear_down()

    def prepare_ssh_autologin(self, ssh_pub_key='~/.ssh/id_rsa.pub'):
        """Prepare server for ssh autologin with ssh ke."""
        ssh_dir = '~/.ssh'
        authorized_keys = 'authorized_keys'

        if not exists(ssh_dir):
            run('mkdir %s' % ssh_dir)

        with cd('~/.ssh'):
            if not exists(authorized_keys):
                run('touch %s && chmod 600 %s' % (authorized_keys,
                                                  authorized_keys))
            if not os.path.exists(os.path.expanduser(ssh_pub_key)):
                print(red('Public key file "%s" not  exist.' % ssh_pub_key))
                return False
            ssh_pub_key_string = open(
                os.path.expanduser(ssh_pub_key), 'r').readline()

            if not contains(authorized_keys, ssh_pub_key_string):
                append(authorized_keys, ssh_pub_key_string)
                print(green('Public key successfully added  in'
                            ' %s.' % authorized_keys))
            else:
                print(magenta(
                    'Public key already in %s.' % authorized_keys))
            run('chmod 600 %s' % authorized_keys)
        run('chmod 700 %s' % ssh_dir)
        return True

    def get_desktop_manager_conf(self):
        result = ''
        for dmc_conf in self.list_desktop_manager_conf:
            obj = dmc_conf()
            append_desktop_manager_conf = getattr(
                obj, 'append_desktop_manager_conf', None)
            if append_desktop_manager_conf:
                result += (
                    '\n### start {section} customization ###\n{script}\n###'
                    ' end {section} customization ###'.format(
                        section=obj.section_desktop_manager_name,
                        script=append_desktop_manager_conf()))
        return '\n{}\n'.format(result)

    def prepare_desktop_manager_conf(self):
        with cd('/etc/mdm/PostLogin/'):
            if exists('Default'):
                run('mv Default Default.bkp')
            run('cp Default.sample Default')
            append('Default', self.get_desktop_manager_conf())
            run('chmod +x Default')

    def update_apt_packages(self):
        run('apt-get update')
        run('apt-get upgrade -y')

    def prepare_python_env(self):
        run('apt-get install python-pip -y')
        run('pip install --upgrade pip setuptools')

    def config_network(self, *args, **kwargs):
        pass

    def prepare_home_skel(self):
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

    def prepare_ldap_client(self):
        run("DEBIAN_FRONTEND=noninteractive apt-get -y install"
            " libpam-ldap nscd")
        run("auth-client-config -t nss -p lac_ldap")
        append("/etc/pam.d/common-session",
               "session required pam_mkhomedir.so skel=/etc/skel umask=0022")
        # while True:
        #     password_1 = getpass(
        #         green("Inserisci la password dell'ldap Manager: "))
        #     password_2 = getpass(
        #         green(
        #             "Inserisci di nuovo la password dell'ldap Manager: "))
        #     if password_1 != password_2:
        #         print(red("Le password non coincidono!"))
        #     else:
        #         ldap_secret = '/etc/ldap.secret'
        #         if not exists(ldap_secret):
        #             run('touch ' + ldap_secret)
        #         append(ldap_secret, password_1)
        #         run('chmod 600 ' + ldap_secret)
        #         run('chown root:root ' + ldap_secret)
        #         break

        put(self.ldap_client_conf_path, '/etc/ldap.conf')


class SicrawebMixin(object):

    java_installers = {
        '32': 'http://openpa.zola.net/static_open_pa/media/uploads/site-4/'
              'software/java/jre-6u23-linux-i586.bin',
        '64': 'http://openpa.zola.net/static_open_pa/media/uploads/site-4/'
              'software/java/jre-6u23-linux-x64.bin'}
    sicraweb_launch_file = 'command.properties'
    sicraweb_launch_content = 'COMMAND=gnome-open '

    def get_sicraweb_launch_file(self, *args, **kwargs):
        return self.sicraweb_launch_file

    def get_sicraweb_launch_content(self, *args, **kwargs):
        return self.sicraweb_launch_content

    def prepare_sicraweb_jre(self, platform='32'):
        java_version = 'jre1.6.0_23'
        java_path = "/usr/lib/jvm"
        if not exists(java_path):
            run('mkdir -p ' + java_path)
        java_local_installer = java_path + '/{}.bin'.format(java_version)
        run('wget -O {} {}'.format(
            java_local_installer, self.java_installers[platform]))
        with cd(java_path):
            run('chmod +x {}.bin'.format(java_version))
            run('sh {}.bin'.format(java_version))
            run('rm {}.bin'.format(java_version))
        java_path += '/' + java_version

        for java_program in ['java', 'javaws']:
            run('update-alternatives --remove-all ' + java_program)
            run('update-alternatives --install "/usr/bin/{java_program}"'
                ' "{java_program}" "{java_path}/bin/{java_program}"'
                ' 1'.format(java_program=java_program, java_path=java_path))
            run('chmod a+x /usr/bin/{java_program}'.format(
                java_program=java_program))
        run('java -version')


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
            run('pip install --upgrade {}'.format(self.pyzenity_installer))
            run('pip install --upgrade --allow-external PyZenity'
                ' --allow-unverified PyZenity pygmount')

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

        # with cd('/etc/mdm/PostLogin/'):
        #     if not exists('Default'):
        #         run('cp Default.sample Default')
        #     if not contains('Default', '.pygmount.rc'):
        #         append(
        #             'Default',
        #             'sed -i -e "s/\\\$USER/${LOGNAME}/g" $HOME/.pygmount.rc',
        #             partial=True)


class RdesktopMixin(object):

    def prepare_rdesktop(self):
        run('sudo apt-get install -y libpcsclite1 pcscd pcsc-tools'
            ' libacr38u libacr38ucontrol0 libccid rdesktop')


class BrowsersMixin(object):
    chrome_installers = {
        '32': 'http://openpa.zola.net/static_open_pa/media/uploads/site-4/'
              'software/google_chrome/google-chrome-stable_current_i386.deb',
        '64': 'http://openpa.zola.net/static_open_pa/media/uploads/site-4/'
              'software/google_chrome/google-chrome-stable_current_amd64.deb'
    }

    def prepare_firefox(self):
        run('apt-get install -y firefox-locale-it')

    def prepare_chromium(self):
        run('apt-get install -y chromium-browser'
            ' chromium-codecs-ffmpeg-extra')

    def prepare_chrome(self, platform):
        run('wget -O google-chrome.deb {}'.format(
            self.chrome_installers[platform]))
        run('dpkg -i google-chrome.deb')

    def prepare_browsers(self, platform):
        self.prepare_firefox()
        self.prepare_chromium()
        self.prepare_chrome(platform)


class MateMixin(object):

    token_file = '.newage_token.txt'

    def mate_check_config_files(self):
        result = [True, '']
        for file_config_path in [self.mate_config_post_login,
                                 self.mate_config_post_session]:
            if not os.path.exists(file_config_path):
                result[0] = False
                result[1] += (
                    'Mate warning: file {} non presente'.format(
                        file_config_path))
        return tuple(result)

    @property
    def mate_config_path(self):
        return os.path.join(
            os.path.dirname(__file__), '..', 'conf', 'mate', 'mdm')

    @property
    def mate_config_post_login(self):
        return os.path.join(self.mate_config_path, 'PostLogin', 'Default')

    @property
    def mate_config_post_session(self):
        return os.path.join(self.mate_config_path, 'PostSession', 'Default')

    def prepare_mate_env(self):
        self.mate_check_config_files()
        self.prepare_post_login()
        self.prepare_post_session()

    def prepare_post_login(self):
        with cd('/etc/mdm/PostLogin/'):
            if exists('Default'):
                run('mv Default Default.backup')
            run('cp Default.sample Default')
            with open(self.mate_config_post_login) as f:
                append('Default', '\n' + ''.join(f.readlines()))
            run('touch {}'.format(self.token_file))

    def prepare_post_session(self):
        with cd('/etc/mdm/PostSession/'):
            if exists('Default'):
                if not exists(self.token_file):
                    run('mv Default Default.sample')
                else:
                    run('mv Default Default.backup')
                run('touch Default')
                content = run('cat Default.sample', quiet=True)
                with open(self.mate_config_post_session) as f:
                    append('Default',
                           content.replace('\r', '').replace(
                               'exit 0',
                               '{}\nexit0'.format(''.join(f.readlines()))),
                           shell=True)
                run('chmod +x Default')
            run('touch {}'.format(self.token_file))


class PamMountMixin(object):

    pammount_volumes_definitios = []

    def prepare_pam_mount(self):
        run('apt-get install -y libpam-mount')
        sed(
            '/etc/security/pam_mount.conf.xml'
            '<!-- Volume definitions -->',
            '<!-- Volume definitions -->\n{}'.format('\n'.join(
                self.pammount_volumes_definitios)))

