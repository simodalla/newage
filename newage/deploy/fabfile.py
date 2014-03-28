# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, with_statement

import os

from fabric.api import (local, env, abort, prompt, task, require)

from linux.core import Linux
from linux.mint.core import Mint13, Mint16

ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
GET_PIP_FILE = 'https://raw.github.com/pypa/pip/master/contrib/get-pip.py'


VMS_LOCAL_PATH = os.path.expanduser(
    '~/Documents/Virtual\ Machines.localized/') + '{vm_name}.vmwarevm/'


if len(env.hosts) == 0:
    env.hosts = ['mone.local']

#env.hosts = ['172.16.102.97']
#env.user = 'sistemiinformatici'
# sudo_user = 'simo'


def check_platform(platform):
    Linux.check_platform(platform)


def waiting_for(attempts=9, interval=1):
    Linux.waiting_for(attempts, interval)


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
def set_linux(version='mint13', platform='32'):
    if version == 'mint13':
        env.linux = Mint13(platform=platform)
    elif version == 'mint16':
        env.linux = Mint16(platform=platform)
    else:
        abort("Wrong linux version: {}".format(version))


@task
def deploy(platform='32'):
    require('linux', provided_by=['set_linux'])
    env.linux.get_pip_file = GET_PIP_FILE
    env.linux.ldap_client_conf_path = '{}/conf/ldap/ldap.conf'.format(
        ABSOLUTE_PATH)
    env.linux.deploy()
