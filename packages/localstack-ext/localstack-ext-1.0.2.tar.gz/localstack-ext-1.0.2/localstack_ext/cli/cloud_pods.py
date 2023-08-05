_M='Merge the injecting state with the current application runtime.'
_L='--merge'
_K='--version'
_J='--message'
_I='--local'
_H='--services'
_G='[red]Error:[/red] Input the services as a comma-delimited list'
_F='Name of the Cloud Pod.'
_E='name'
_D='--name'
_C='-n'
_B=True
_A=False
import os,sys,traceback
from typing import Dict,List,Optional,Set
import click
from click import Context
from localstack.cli import console
from localstack.utils.analytics.cli import publish_invocation
from localstack_ext.bootstrap.pods.utils.common import is_comma_delimited_list
from localstack_ext.cli.click_utils import clean_command_dict,command_require_at_least_open_option,print_pods,required_if_not_cached
from localstack_ext.cli.tree_view import TreeRenderer
class PodsCmdHandler(click.Group):
	def invoke(self,ctx):
		try:return super(PodsCmdHandler,self).invoke(ctx)
		except Exception as exc:
			if isinstance(exc,click.exceptions.Exit):raise
			click.echo(f"Error: {exc}")
			if ctx.parent and ctx.parent.params.get('debug'):click.echo(traceback.format_exc())
			ctx.exit(1)
def _cloud_pod_initialized(pod_name):
	from localstack_ext.bootstrap import pods_client
	if not pods_client.is_initialized(pod_name=pod_name):console.print(f"[red]Error:[/red] Could not find local CloudPods instance '{pod_name}'");return _A
	return _B
def api_key_configured():A='LOCALSTACK_API_KEY';return _B if os.environ.get(A)and os.environ.get(A).strip()else _A
@click.group(name='pod',help='Manage the state of your instance via Cloud Pods.',cls=PodsCmdHandler,context_settings=dict(max_content_width=120))
def pod():
	from localstack_ext.bootstrap.licensing import is_logged_in
	if api_key_configured():
		from localstack_ext.bootstrap import licensing
		with licensing.prepare_environment():console.print('pro activation done')
	else:console.print('[red]Error:[/red] pod commands currently require LOCALSTACK_API_KEY set, please set and try again.');sys.exit(1)
	try:import moto
	except ImportError:console.print('[red]Error:[/red] pod commands currently require runtime dependencies. Please run `pip install localstack\\[runtime]` and try again.');sys.exit(1)
	if not is_logged_in():console.print('[red]Error:[/red] not logged in, please log in first');sys.exit(1)
@pod.command(name='config',help='Configure a set of parameters for all Cloud Pods commands.',cls=command_require_at_least_open_option())
@click.option(_C,_D,help=_F)
@click.option('-s',_H,help='Comma-delimited list of services or `all` to enable all (default).')
@publish_invocation
def cmd_pod_config(name,services):
	from localstack_ext.bootstrap import pods_client
	if services and not is_comma_delimited_list(services):console.print(_G);return _A
	options=clean_command_dict(options=dict(locals()),keys_to_drop=['pods_client']);pods_client.save_pods_config(options=options)
@pod.command(name='delete',help='Delete a Cloud Pod.')
@click.option(_C,_D,help=_F,cls=required_if_not_cached(_E))
@click.option('-l',_I,help='Delete only the local Cloud Pod, leaving the remote copy intact',is_flag=_B,default=_A)
@publish_invocation
def cmd_pod_delete(name,local):
	from localstack_ext.bootstrap import pods_client;result=pods_client.delete_pod(pod_name=name,remote=not local)
	if result:console.print(f"Successfully deleted {name}")
	else:console.print(f"[yellow]{name} not available locally[/yellow]")
@pod.command(name='commit',help='Commit a snapshot of the LocalStack running instance.')
@click.option('-m',_J,help='Add a comment describing the snapshot.')
@click.option(_C,_D,help=_F,cls=required_if_not_cached(_E))
@click.option('-s',_H,help='Comma-delimited list of services to push in the pods (all, by default).')
@publish_invocation
def cmd_pod_commit(message,name,services):
	from localstack_ext.bootstrap import pods_client
	if services and not is_comma_delimited_list(services):console.print(_G);return _A
	service_list=[x.strip()for x in services.split(',')]if services else None;pods_client.commit_state(pod_name=name,message=message,services=service_list);console.print('Successfully committed the current state')
@pod.command(name='push',help='Create a new version of a Cloud Pod from the latest snapshot.\nA snapshot is created if it does not exists yet.')
@click.option(_I,'-l',default=_A,is_flag=_B,help='Create the Cloud Pod version only locally, without pushing to remote')
@click.option('-m',_J,help='Add a comment describing the version.')
@click.option(_C,_D,help=_F,cls=required_if_not_cached(_E))
@click.option('-s',_H,help='Comma-delimited list of services to push in the pods (all by default).')
@click.option('--overwrite',help='Overwrite a version with the content from the latest snapshot of the selected version.',type=bool,default=_A)
@click.option('-v',_K,help='Version to overwrite. Works with `--overwrite`.',type=int)
@publish_invocation
def cmd_pod_push(message,name,local,services,overwrite,version):
	from localstack_ext.bootstrap import pods_client
	if services and not is_comma_delimited_list(services):console.print(_G);return _A
	service_list=[x.strip()for x in services.split(',')]if services else None
	if overwrite:
		result=pods_client.push_overwrite(version=version,pod_name=name,comment=message,services=service_list)
		if result:console.print('Successfully overwritten state of version ')
		return
	result=pods_client.push_state(pod_name=name,comment=message,register=not local,services=service_list);console.print('Successfully pushed the current state')
	if not local:
		if result:console.print(f"Successfully registered {name} with remote!")
		else:console.print(f"[red]Error:[/red] Pod with name {name} is already registered")
@pod.command(name='inject',help='Inject the state from a locally available Cloud Pod version into the application runtime.')
@click.option(_L,is_flag=_B,default=_A,help=_M)
@click.option('-v',_K,default='-1',type=int,help='Version to inject (most recent one by default).')
@click.option(_C,_D,help='Name of the cloud pod.',cls=required_if_not_cached(_E))
@publish_invocation
def cmd_pod_inject(merge,version,name):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	result=pods_client.inject_state(pod_name=name,version=version,merge=merge)
	if result:console.print('[green]Successfully Injected Pod State[/green]')
	else:console.print('[red]Failed to Inject Pod State[/red]')
@click.option('--fetch',default=_A,is_flag=_B,help='Only fetch the Cloud Pod from the remote platform.')
@click.option(_L,is_flag=_B,default=_A,help=_M)
@click.option(_C,_D,help='Name of the cloud pod',cls=required_if_not_cached(_E))
@pod.command(name='pull',help='Incorporate the state of a Cloud Pod into the application runtime.')
@publish_invocation
def cmd_pod_pull(name,fetch,merge):from localstack_ext.bootstrap import pods_client;pods_client.pull_state(pod_name=name,inject=not fetch,merge=merge)
@pod.command(name='list',help='List all available Cloud Pods.')
@click.option(_I,'-l',help='List also locally available Cloud Pods.',is_flag=_B,default=_A)
@publish_invocation
def cmd_pod_list_pods(local):
	from localstack_ext.bootstrap import pods_client;pods=pods_client.list_pods(local=local)
	if not pods:console.print(f"[yellow]No pods available {'locally'if local else''}[/yellow]")
	print_pods(pods)
@pod.command(name='versions',help='List all available versions for a Cloud Pod.')
@click.option(_C,_D,help=_F,cls=required_if_not_cached(_E))
@publish_invocation
def cmd_pod_versions(name):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	version_list=pods_client.get_version_summaries(pod_name=name);result='\n'.join(version_list);console.print(result)
@pod.command(name='inspect',help='Inspect the contents of a Cloud Pod.')
@click.option(_C,_D,help=_F,cls=required_if_not_cached(_E))
@click.option('-f','--format',help='Format (curses, rich, json).',default='curses')
@publish_invocation
def cmd_pod_inspect(name,format):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	result=pods_client.get_version_metamodel(pod_name=name,version=-1);skipped_services=['cloudwatch']
	for (account,details) in result.items():result[account]={k:v for(k,v)in details.items()if k not in skipped_services}
	TreeRenderer.get(format).render_tree(result)