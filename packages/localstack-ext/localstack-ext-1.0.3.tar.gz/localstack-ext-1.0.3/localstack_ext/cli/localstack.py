_B='[red]Error:[/red] '
_A=True
import logging,os,sys
from typing import Any,List,Optional
import click
from localstack.cli import LocalstackCli,LocalstackCliPlugin,console
from localstack.utils.analytics.cli import publish_invocation
from localstack_ext.bootstrap.licensing import is_logged_in
from ..bootstrap.pods.utils.common import is_comma_delimited_list
from .cloud_pods import pod
from .extensions import extensions
class ProCliPlugin(LocalstackCliPlugin):
	name='pro'
	def should_load(A):return is_logged_in()
	def attach(B,cli):A=cli.group;A.add_command(cmd_logout);A.add_command(cmd_reset);A.add_command(daemons);A.add_command(dns);A.add_command(pod);A.add_command(extensions)
class LoginCliPlugin(LocalstackCliPlugin):
	name='login'
	def attach(B,cli):A=cli.group;A.add_command(cmd_login);A.add_command(cmd_pod_login)
@click.group(name='daemons',help='Manage local daemon processes')
def daemons():0
@click.command(name='login',help='Log in with your account credentials')
@click.option('--username',help='Username for login')
@publish_invocation
def cmd_login(username):
	from localstack_ext.bootstrap import auth
	try:auth.login(username);console.print('successfully logged in')
	except Exception as A:console.print('authentication error: %s'%A)
@click.command(name='reset',help='Reset the service states of the running LocalStack container')
@click.option('-p','--persistence',help='Reset the persistence directory (set with PERSISTENCE=1)',is_flag=_A,default=False)
@click.option('-s','--services',help='Comma-delimited list of services to reset. By default, it resets everything')
@publish_invocation
def cmd_reset(persistence,services):
	A=services;from localstack_ext.bootstrap import pods_client as B
	if A and not is_comma_delimited_list(A):console.print('[red]Error:[/red] Input the services as a comma-delimited list');return False
	C=[B.strip()for B in A.split(',')]if A else None;B.reset_local_state(reset_persistence=persistence,services=C)
@click.command(name='pod',hidden=_A,context_settings=dict(ignore_unknown_options=_A,allow_extra_args=_A))
def cmd_pod_login():
	if not is_logged_in():console.print('Please login to use Cloud Pods')
@click.command(name='logout',help='Log out and delete any session tokens')
@publish_invocation
def cmd_logout():
	from localstack_ext.bootstrap import auth
	try:auth.logout();console.print('successfully logged out')
	except Exception as A:console.print('logout error: %s'%A)
@daemons.command(name='start',help='Start local daemon processes')
@publish_invocation
def cmd_daemons_start():from localstack_ext.bootstrap import local_daemon as A;console.log('Starting local daemons processes ...');B=A.start_in_background();B.join()
@daemons.command(name='stop',help='Stop local daemon processes')
@publish_invocation
def cmd_daemons_stop():from localstack_ext.bootstrap import local_daemon as A;console.log('Stopping local daemons processes ...');A.kill_servers()
@daemons.command(name='log',help='Show log of daemon process')
@publish_invocation
def cmd_daemons_log():
	from localstack_ext.bootstrap import local_daemon as B;A=B.get_log_file_path()
	if not os.path.isfile(A):console.print('no log found')
	else:
		with open(A,'r')as C:
			for D in C:sys.stdout.write(D);sys.stdout.flush()
@click.group(name='dns',help='Manage DNS settings of your host')
def dns():0
@dns.command(name='systemd-resolved',help='Manage DNS settings of systemd-resolved (Ubuntu, Debian etc.)')
@click.option('--revert',is_flag=_A,help='Revert systemd-resolved settings for the docker interface')
@publish_invocation
def cmd_dns_systemd(revert):import localstack_ext.bootstrap.dns_utils;from localstack_ext.bootstrap.dns_utils import configure_systemd as A;console.print('Configuring systemd-resolved...');B=localstack_ext.bootstrap.dns_utils.LOG.name;localstack_ext.bootstrap.dns_utils.LOG=ConsoleLogger(B);A(revert)
class ConsoleLogger(logging.Logger):
	def __init__(A,name):super(ConsoleLogger,A).__init__(name)
	def info(B,msg,*A,**C):console.print(msg%A)
	def warning(B,msg,*A,**C):console.print('[red]Warning:[/red] ',msg%A)
	def error(B,msg,*A,**C):console.print(_B,msg%A)
	def exception(B,msg,*A,**C):console.print(_B,msg%A);console.print_exception()