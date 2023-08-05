_C='uninstall'
_B='install'
_A='bin/python'
import os
from typing import List
import click
from click import ClickException
from localstack.utils.analytics.cli import publish_invocation
@click.group(name='extensions',help='Manage LocalStack extensions (beta)')
def extensions():0
@extensions.command('init')
@publish_invocation
def cmd_extensions_init():_run_localstack_container_command(['.venv/bin/python','-m','localstack_ext.bootstrap.extensions','init'])
def assert_venv_initialized():
	from localstack import config as A;from localstack_ext.bootstrap.extensions import repository as B
	if os.path.exists(os.path.join(A.VOLUME_DIR,'lib',B.VENV_DIRECTORY)):raise ClickException('extensions dir not initialized, please run `localstack extensions init` first or check if `LOCALSTACK_VOLUME_DIR` is set correctly')
@extensions.command(_B)
@click.argument('name',required=True)
@publish_invocation
def cmd_extensions_install(name):from localstack import config as A;from localstack_ext.bootstrap.extensions import repository as B;assert_venv_initialized();C=os.path.join(A.Directories.for_container().var_libs,B.VENV_DIRECTORY,_A);_run_localstack_container_command([C,'-m','pip',_B,name])
@extensions.command(_C,help='Remove a LocalStack extension')
@click.argument('name',required=True)
@publish_invocation
def cmd_extensions_uninstall(name):from localstack import config as A;from localstack_ext.bootstrap.extensions import repository as B;assert_venv_initialized();C=os.path.join(A.Directories.for_container().var_libs,B.VENV_DIRECTORY,_A);_run_localstack_container_command([C,'-m','pip',_C,'-y',name])
def _run_localstack_container_command(cmd):
	from localstack import config as D,constants as B;from localstack.utils import docker_utils as A;C=A.DOCKER_CLIENT.create_container(image_name=B.DOCKER_IMAGE_NAME,entrypoint='',remove=True,command=cmd,mount_volumes=[(D.VOLUME_DIR,B.DEFAULT_VOLUME_DIR)]);A.DOCKER_CLIENT.start_container(C);E=A.DOCKER_CLIENT.stream_container_logs(C)
	for F in E:print(F.decode('utf-8'),end='')