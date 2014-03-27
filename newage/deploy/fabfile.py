# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, with_statement

import os
from getpass import getpass

from fabric.api import (local, env, run, abort, put, prompt, task,
                        prefix, cd, settings, sudo)
from fabric.contrib.files import exists, append, contains
from fabric import colors

from linux.core import Linux
from linux.mint.core import Mint13

ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
GET_PIP_FILE = 'https://raw.github.com/pypa/pip/master/contrib/get-pip.py'
JAVA_INSTALLERS = {
    '32': 'http://openpa.zola.net/static_open_pa/media/uploads/site-4/'
          'software/java/jre-6u23-linux-i586.bin',
    '64': 'http://openpa.zola.net/static_open_pa/media/uploads/site-4/'
          'software/java/jre-6u23-linux-x64.bin'}
RDESKTOP_INSTALLERS = {
    '32': 'http://ftp.de.debian.org/debian/pool/main/r/rdesktop/'
          'rdesktop_1.7.1-1_i386.deb',
    '64': 'http://ftp.de.debian.org/debian/pool/main/r/rdesktop/'
          'rdesktop_1.7.1-1_amd64.deb'}
VMS_LOCAL_PATH = os.path.expanduser(
    '~/Documents/Virtual\ Machines.localized/') + '{vm_name}.vmwarevm/'
CHROME_INSTALLERS = {
    '32': 'http://openpa.zola.net/static_open_pa/media/uploads/site-4/'
          'software/google_chrome/google-chrome-stable_current_i386.deb',
    '64': 'http://openpa.zola.net/static_open_pa/media/uploads/site-4/'
          'software/google_chrome/google-chrome-stable_current_amd64.deb'
}

if len(env.hosts) == 0:
    env.hosts = ['mone.local']

#env.hosts = ['172.16.102.97']
#env.user = 'sistemiinformatici'
# sudo_user = 'simo'


def check_platform(platform):
    Linux.check_platform(platform)


def waiting_for(attempts=9, interval=1):
    Linux.waiting_for(attempts, interval)


@task
def prepare_ssh_autologin(ssh_pub_key='~/.ssh/id_rsa.pub'):
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
            print(colors.red('Public key file "%s" not'
                             ' exist.' % ssh_pub_key))
            return False
        ssh_pub_key_string = open(
            os.path.expanduser(ssh_pub_key), 'r').readline()

        if not contains(authorized_keys, ssh_pub_key_string):
            append(authorized_keys, ssh_pub_key_string)
            print(colors.green('Public key successfully added'
                               ' in %s.' % authorized_keys))
        else:
            print(colors.magenta(
                'Public key already in %s.' % authorized_keys))
        run('chmod 600 %s' % authorized_keys)
    run('chmod 700 %s' % ssh_dir)
    return True


@task
def update_apt_packages():
    run('apt-get update')
    run('apt-get upgrade -y')


@task
def prepare_python_env():
    run('apt-get remove python-setuptools python-pip')
    run('wget {}'.format(GET_PIP_FILE))
    run('python get-pip.py')
    run('pip install -U setuptools')


@task
def prepare_rdesktop(platform='32'):
    check_platform(platform)
    run('sudo apt-get install -y libpcsclite1 pcscd pcsc-tools'
        ' libacr38u libacr38ucontrol0 rdesktop')
    run('wget {}'.format(RDESKTOP_INSTALLERS[platform]))
    run('dpkg -i {}'.format(RDESKTOP_INSTALLERS[platform].split('/')[-1]))


@task
def prepare_chrome(platform='32'):
    check_platform(platform)
    run('apt-get install -y chromium-browser'
        ' chromium-codecs-ffmpeg-extra')
    run('wget -O google-chrome.deb {}'.format(CHROME_INSTALLERS[platform]))
    run('dpkg -i google-chrome.deb')


@task
def prepare_browsers(platform='32'):
    run('apt-get install -y firefox-locale-it')
    prepare_chrome(platform)


@task
def prepare_java(platform='32'):
    check_platform(platform)
    java_version = 'jre1.6.0_23'
    java_path = "/usr/lib/jvm"
    if not exists(java_path):
        run('mkdir -p ' + java_path)
    java_local_installer = java_path + '/{}.bin'.format(java_version)
    run('wget -O {} {}'.format(
        java_local_installer, JAVA_INSTALLERS[platform]))
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


@task
def prepare_ldap_client():
    run("DEBIAN_FRONTEND=noninteractive apt-get -y install libpam-ldap nscd")
    run("auth-client-config -t nss -p lac_ldap")
    append("/etc/pam.d/common-session",
           "session required pam_mkhomedir.so skel=/etc/skel umask=0022")
    while True:
        password_1 = getpass(
            colors.green("Inserisci la password dell'ldap Manager: "))
        password_2 = getpass(
            colors.green("Inserisci di nuovo la password dell'ldap Manager: "))
        if password_1 != password_2:
            print(colors.red("Le password non coincidono!"))
        else:
            ldap_secret = '/etc/ldap.secret'
            if not exists(ldap_secret):
                run('touch ' + ldap_secret)
            append(ldap_secret, password_1)
            run('chmod 600 ' + ldap_secret)
            run('chown root:root ' + ldap_secret)
            break

    put('{}/conf/ldap/ldap.conf'.format(ABSOLUTE_PATH), '/etc/ldap.conf')


def vmware_run_cmd(cmd, vm_path, *args):
    vmrun = 'vmrun -T fusion %s %s' % (cmd, vm_path)
    if len(args) > 0:
        vmrun += ' ' + ' '.join(list(args))
    return vmrun


@task
def vm_reset(vm_name, snapshot=None):
    vm_path = VMS_LOCAL_PATH.format(vm_name=vm_name)
    if not snapshot:
        output = local(vmware_run_cmd('listSnapshots', vm_path), capture=True)
        options = {i: snap for i, snap in enumerate(output.split('\n')[1:],
                                                    start=1)}
        options.update({0: '**esci**'})
        option = prompt(
            '\n'.join(['{} - {}'.format(k, options[k]) for k in options]) +
            '\n\nInserisci il numero dello snapshot da ripristinare: ',
            validate=int)
        if option == 0:
            abort('Exit...')
        snapshot = options[option]
    local(vmware_run_cmd('revertToSnapshot', vm_path, snapshot))
    local(vmware_run_cmd('start', vm_path))
    waiting_for()


@task
def deploy_mint_13(platform='32'):
    mint13 = Mint13(platform=platform)
    # prepare_ssh_autologin()
    # sudo("passwd root")
    with settings(user='root'):
        # mint13.config_network()
        # prepare_ssh_autologin()
        # update_apt_packages()
        # prepare_python_env()
        # prepare_rdesktop(platform)
        # prepare_java(platform)
        # prepare_ldap_client()
        # prepare_browsers(platform)
        # mint13.prepare_home_skel()
        # mint13.prepare_virtualenv_env()
        mint13.prepare_pygmount()
    # sudo("passwd -dl root")


