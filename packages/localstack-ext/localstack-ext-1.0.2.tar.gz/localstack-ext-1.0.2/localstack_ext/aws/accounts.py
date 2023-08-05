import logging,threading
from dataclasses import dataclass
from typing import Any,Callable,Dict
from localstack import config as localstack_config
from localstack.aws.accounts import REQUEST_CTX_TLS,get_aws_account_id,get_default_account_id
from localstack.constants import LS_LOG_TRACE_INTERNAL
from localstack.utils.patch import patch
def _patch_moto_backend_dict():
	H='us-east-1';G='global';import moto as C
	@dataclass(frozen=True)
	class F:account_id:str;service_name:str
	A={}
	@patch(C.core.utils.BackendDict.__getitem__)
	def B(__getitem__,self,region):
		D=region;B=self
		if D in(G,H):return __getitem__(B,D)
		I=get_aws_account_id();E=F(I,B.fn.__name__)
		if E not in A:A[E]=C.core.utils.BackendDict(B.fn,B.service_name)
		return __getitem__(A[E],D)
	@patch(C.core.utils.BackendDict.__contains__)
	def D(__contains__,self,region):
		B=region
		if B in(G,H):return __contains__(self,B)
		D=get_aws_account_id();C=F(D,self.fn.__name__)
		if C not in A:return False
		return __contains__(A[C],B)
def _patch_account_id_resolver():
	import localstack as A
	def B():
		try:return REQUEST_CTX_TLS.account_id
		except AttributeError:
			if localstack_config.LS_LOG and localstack_config.LS_LOG==LS_LOG_TRACE_INTERNAL:logging.debug('No Account ID in thread-local storage for thread %s',threading.current_thread().ident)
			return get_default_account_id()
	A.aws.accounts.account_id_resolver=B
def _patch_get_account_id_from_access_key_id():
	from localstack.aws import accounts as A
	def B(access_key_id):A=C(access_key_id);REQUEST_CTX_TLS.account_id=A;return A
	C=A.get_account_id_from_access_key_id;A.get_account_id_from_access_key_id=B