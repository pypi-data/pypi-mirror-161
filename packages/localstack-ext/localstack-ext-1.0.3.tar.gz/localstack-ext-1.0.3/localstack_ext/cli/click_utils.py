from typing import Any,Dict,List,Mapping,Set,Tuple
import click
from click import Context
from localstack.cli import console
def required_if_not_cached(option_key):
	B=option_key
	class A(click.Option):
		def handle_parse_result(C,ctx,opts,args):
			A=opts;from localstack_ext.bootstrap import pods_client as E;F=C.name in A
			if not F:
				D=E.get_pod_name_from_config()
				if not D:raise click.MissingParameter(f"Parameter `--{B}` unspecified. Call with `--{B}` or set the parameter with `localstack pod config --name <name>`")
				A[C.name]=D
			return super().handle_parse_result(ctx,A,args)
	return A
def command_require_at_least_open_option():
	class A(click.Command):
		def invoke(B,ctx):
			C=ctx.params.values()
			if not any(C):raise click.ClickException('Specify at least one option for the config command')
			super(A,B).invoke(ctx)
	return A
def clean_command_dict(options,keys_to_drop=None):return{A:B for(A,B)in options.items()if A not in keys_to_drop and B}
def print_pods(pods):
	from rich.table import Table;A=Table(show_header=True,header_style='bold');A.add_column('local/remote');A.add_column('Name')
	for (C,B) in pods.items():A.add_row('local+remote'if len(B)>1 else list(B)[0],C)
	console.print(A)