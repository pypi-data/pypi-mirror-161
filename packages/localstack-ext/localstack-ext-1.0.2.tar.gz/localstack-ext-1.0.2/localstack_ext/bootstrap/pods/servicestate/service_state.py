from __future__ import annotations
import hashlib,logging
from typing import Callable,Dict,List,Optional,Set
from localstack_ext.bootstrap.pods.servicestate.service_state_types import AssetByNameType,AssetByServiceType,AssetNameType,AssetValueType,BackendState,ServiceKey,ServiceNameType
from localstack_ext.bootstrap.pods.utils.common import marshall_backend
from localstack_ext.bootstrap.pods.utils.merge_utils import get_merge_function_for_assets
from localstack_ext.bootstrap.state_merge import merge_object_state
LOG=logging.getLogger(__name__)
class ServiceState:
	def __init__(A):A.state={};A.assets={}
	def put_service_state(A,service_state):
		B=service_state
		for C in B.state.values():A.put_backend(C)
		for (D,E) in B.assets.items():A.put_assets(D,E)
	def put_backend(B,backend_state):A=backend_state;B.state[A.key]=A
	def put_asset(A,service_name,asset_name,asset_value):B=service_name;C=A.assets.get(B,{});C[asset_name]=asset_value;A.assets[B]=C
	def put_assets(A,service_name,assets_by_name):A.assets[service_name]=assets_by_name
	def merge(C,inject,ancestor=None):
		D=inject;B=ancestor;merge_object_state(C.state,D.state,B.state if B else None);I={*C.assets.keys(),*D.assets.keys(),*(B.assets.keys()if B else{})}
		for A in I:
			E=A in C.assets;F=A in D.assets;G=A in B.assets if B else False;J=not E and F and not G;K=E and not F and G
			if J:C.assets[A]=D.assets[A]
			elif K:del C.assets[A]
			else:H=C.assets.get(A);L=D.assets.get(A,{});M=B.assets.get(A,{})if B else None;N=get_merge_function_for_assets(service=A)or merge_object_state;N(H,L,M);C.assets[A]=H
	def is_empty(A):return len(A.state)==0 and len(A.assets)==0
	def get_services(C):
		A=set()
		for B in C.state:A.add(B.service)
		for B in C.assets:A.add(B)
		return list(A)
	def get_backends_for_service(A,service):return[C for(B,C)in A.state.items()if B.service==service]
	def compute_hash_on_state(A):
		B=hashlib.sha1();D=sorted(A.state.keys())
		for E in D:
			C=A.state.get(E);F=sorted(C.backends.keys())
			for G in F:H=C.backends.get(G);B.update(marshall_backend(H))
		return B.hexdigest()
	def __str__(A):return f"Backends: {A.state.__str__()}\nAssets: {A.assets.__str__()}"