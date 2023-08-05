_L='presigned_url_metadata'
_K='presigned_url_state'
_J='qualifying_name'
_I='max_version'
_H='api_states'
_G='presigned_urls'
_F='services'
_E='storage_uuid'
_D='pod_name'
_C=False
_B=None
_A=True
import json,logging,os,re
from abc import ABCMeta,abstractmethod
from enum import Enum
from shutil import make_archive
from typing import Dict,List,Optional,Set,Union
import requests
from localstack import config,constants
from localstack.utils.common import cp_r,disk_usage,download,load_file,new_tmp_dir,new_tmp_file,retry,rm_rf,safe_requests,save_file,to_str
from localstack.utils.docker_utils import DOCKER_CLIENT
from requests import Response
from localstack_ext.bootstrap.licensing import get_auth_headers
from localstack_ext.bootstrap.pods.models import Serialization,Version
from localstack_ext.bootstrap.pods.pods_api import PodsApi
from localstack_ext.bootstrap.pods.servicestate.service_state import ServiceState
from localstack_ext.bootstrap.pods.utils import remote_utils
from localstack_ext.bootstrap.pods.utils.adapters import ServiceStateMarshaller
from localstack_ext.bootstrap.pods.utils.common import PodsConfigContext
from localstack_ext.bootstrap.pods.utils.metamodel_utils import CommitMetamodelUtils
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR
from localstack_ext.constants import API_PATH_PODS
LOG=logging.getLogger(__name__)
PERSISTED_FOLDERS=[API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR]
class PodInfo:
	def __init__(A,name=_B,pod_size=0):A.name=name;A.pod_size=pod_size;A.pod_size_compressed=0;A.persisted_resource_names=[]
class PodLocation(Enum):REMOTE='remote';LOCAL='local'
def get_state_zip_from_instance(get_content=_C,services=_B):
	B=services;C=f"{get_pods_endpoint()}/state";E=','.join(B)if B else'';A=requests.get(C,params={_F:E})
	if A.status_code>=400:raise Exception(f"Unable to get local pod state via management API {C} (code {A.status_code}): {A.content}")
	if get_content:return A.content
	D=f"{new_tmp_file()}.zip";save_file(D,A.content);return D
class CloudPodsManager(metaclass=ABCMeta):
	def __init__(A,pod_name):B=pod_name;A.pod_name=B;C=PodsConfigContext(pod_name=B);A.pods_api=PodsApi(C)
	@abstractmethod
	def init(self):...
	@abstractmethod
	def delete(self,remote):...
	@abstractmethod
	def push(self,comment=_B,services=_B):...
	@abstractmethod
	def push_overwrite(self,version,comment=_B,services=_B):...
	@abstractmethod
	def pull(self,inject=_A,merge=_C):...
	@abstractmethod
	def commit(self,message,services=_B):...
	@abstractmethod
	def inject(self,version,merge):...
	@abstractmethod
	def get_version_summaries(self):...
	@abstractmethod
	def version_metamodel(self,version):...
	@abstractmethod
	def set_version(self,version,inject_version_state,reset_state,commit_before):...
	@abstractmethod
	def list_version_commits(self,version):...
	@abstractmethod
	def get_commit_diff(self,version,commit):...
	@abstractmethod
	def register_remote(self,ci_pod=_B):...
	@abstractmethod
	def rename_pod(self,current_pod_name,new_pod_name):...
	@abstractmethod
	def list_pods(self,only_local):...
	@staticmethod
	def restart_container():
		LOG.info('Restarting LocalStack instance with updated persistence state - this may take some time ...');B={'action':'restart'};A='%s/health'%config.get_edge_url()
		try:requests.post(A,data=json.dumps(B))
		except requests.exceptions.ConnectionError:pass
		def C():LOG.info('Waiting for LocalStack instance to be fully initialized ...');B=requests.get(A);C=json.loads(to_str(B.content));D=[A for(B,A)in C[_F].items()];assert set(D)=={'running'}
		retry(C,sleep=3,retries=10)
	def get_pod_info(C,pod_data_dir=_B):
		A=pod_data_dir;B=PodInfo(C.pod_name)
		if A:B.pod_size=disk_usage(A);B.persisted_resource_names=get_persisted_resource_names(A)
		return B
class CloudPodsVersionManager(CloudPodsManager):
	def __init__(A,pod_name):super().__init__(pod_name)
	@staticmethod
	def parse_pod_name_from_qualifying_name(qualifying_name):return qualifying_name.split(PODS_NAMESPACE_DELIM,1)[1]
	@staticmethod
	def _prepare_archives_from_pre_signed_urls(content):
		A=new_tmp_file();B=content.get(_G);I=B.get('version_space_url');download(url=I,path=A);C={};D={};J=B.get('meta_state_urls')
		for (E,F) in J.items():G=new_tmp_file();H=new_tmp_file();K=F['meta'];L=F['state'];download(K,G);download(L,H);D[E]=G;C[E]=H
		return A,D,C
	@classmethod
	def _get_max_version_for_pod_from_platform(B,pod_name,auth_headers):
		C=CloudPodsVersionManager.create_platform_url(pod_name);A=safe_requests.get(url=C,headers=auth_headers);D='Failed to get version information from platform.. aborting'
		if not B._check_response(A,message=D,raise_error=_A):return
		E=json.loads(A.content);F=int(E[_I]);return F
	def _add_state_to_cloud_pods_store(A,extract_assets=_C,services=_B):
		B=services
		if not A.pods_api.config_context.is_initialized():LOG.debug('No Cloud Pod instance detected in the local context - unable to add state');return
		B=B or A.pods_api.config_context.get_services_from_config();F=get_state_zip_from_instance(get_content=_A,services=B);D=ServiceStateMarshaller.unmarshall(F,raw_bytes=_A)
		for (C,G) in D.state.items():
			for (H,I) in G.backends.items():A.pods_api.create_state_file_from_fs(file_name=H,service=C.service,region=C.region,root=_H,account_id=C.account_id,serialization=Serialization.MAIN,object=I)
		if extract_assets:
			for (J,K) in D.assets.items():
				for (E,L) in K.items():A.pods_api.create_state_file_from_fs(rel_path=E,file_name=os.path.basename(E),service=J,region='NA',root='assets',account_id='NA',serialization=Serialization.MAIN,object=L)
		M=CommitMetamodelUtils.get_metamodel_from_instance();A.pods_api.add_metamodel_to_current_revision(M)
	def _pull_versions(A,auth_headers,required_versions):
		E=A.create_platform_url(f"{A.pod_name}/data?versions={required_versions}");D=safe_requests.get(url=E,headers=auth_headers);F='Failed to pull requested versions from platform (code <status_code>)'
		if not A._check_response(D,message=F,raise_error=_A):return
		B=json.loads(D.content);G={_E:B.get(_E),_J:B.get(_D)};remote_utils.create_remote_info_file(remote_info=G,config_context=A.pods_api.config_context);C=CloudPodsVersionManager._prepare_archives_from_pre_signed_urls(B);H=C[0];I=C[1];J=C[2];A.pods_api.merge_from_remote(version_space_archive=H,meta_archives=I,state_archives=J)
	def init(A):A.pods_api.init(pod_name=A.pod_name)
	def delete(A,remote):
		C=A.pods_api.config_context.cloud_pods_root_dir;B=os.path.join(C,A.pod_name)
		if os.path.isdir(B):rm_rf(B);return _A
		if remote:0
		return _C
	def _push_to_remote(A,url):
		C=get_auth_headers();B=safe_requests.post(url=url,headers=C);D='Failed to get presigned URLs to upload new version.. aborting'
		if not A._check_response(B,message=D):return
		E=json.loads(B.content);F=E.get(_G);A.pods_api.upload_version_and_product_space(presigned_urls=F)
	def push(A,comment=_B,services=_B):
		D=comment;A.pods_api.set_pod_context(A.pod_name);A._add_state_to_cloud_pods_store(extract_assets=_A,services=services);B:0;C=A.pods_api.get_head().version_number
		if A.pods_api.is_remotely_managed():
			E=get_auth_headers();F=A._get_max_version_for_pod_from_platform(pod_name=A.pod_name,auth_headers=E);B=C<F
			if B:A.pull()
			A.pods_api.push(comment=D);G=A.create_platform_url(f"{A.pod_name}/data?version={C}");A._push_to_remote(url=G)
		else:H=A.pods_api.get_max_version_no();B=C<H;I=A.pods_api.push(comment=D);LOG.debug("Created new version %s for pod '%s'",I.version_number,A.pod_name)
		if B:A.inject(version=-1,merge=_C)
		return PodInfo()
	def push_overwrite(A,version,comment=_B,services=_B):
		B=version;A.pods_api.set_pod_context(pod_name=A.pod_name)
		if B>A.pods_api.get_max_version_no():LOG.warning(f"Version {B} does not exist");return _C
		A._add_state_to_cloud_pods_store(services=services);A.pods_api.push_overwrite(version=B,comment=comment)
		if A.pods_api.is_remotely_managed():C=CloudPodsVersionManager.create_platform_url(f"{A.pod_name}/data?version={B}&overwrite=true");A._push_to_remote(url=C)
		return _A
	def pull(A,inject=_A,merge=_C):
		E=get_auth_headers();B=0
		if A.pod_name in A.pods_api.list_locally_available_pods(only_local=_A):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.get_max_version_no()
		else:A.pods_api.init(pod_name=A.pod_name)
		C=CloudPodsVersionManager._get_max_version_for_pod_from_platform(A.pod_name,E)
		if not C:return
		if C==B:LOG.info('No new version available remotely. Nothing to pull');return
		D=range(B+1,C+1);D=','.join(map(lambda ver:str(ver),D));A._pull_versions(auth_headers=E,required_versions=D)
		if inject:A.inject(version=-1,merge=merge)
	def commit(A,message=_B,services=_B):A.pods_api.set_pod_context(A.pod_name);A._add_state_to_cloud_pods_store(services=services);B=A.pods_api.commit(message=message);LOG.debug('Completed revision: %s',B.hash_ref)
	def _download_version_product(D,version,retain=_C):
		A=version;E=D._get_presigned_url_for_version_product(version=A);F=E.get(_K);G=E.get(_L);B=new_tmp_file();C=new_tmp_file();download(F,B);download(G,C)
		if retain:from localstack_ext.bootstrap.pods.utils.remote_utils import extract_meta_and_state_archives as H;H(meta_archives={A:C},state_archives={A:B},config_context=D.pods_api.config_context)
		return{'metadata_archive':C,'state_archive':B}
	def _get_presigned_url_for_version_product(A,version):
		B=version;C=A.create_platform_url(f"{A.pod_name}/version/product")
		if B!=-1:C+=f"?version={B}"
		E=get_auth_headers();D=safe_requests.get(C,headers=E);F=f"Failed to retrieve presigned URL from remote for version {B} of pod {A.pod_name}"
		if not A._check_response(D,message=F,raise_error=_A):return
		return json.loads(D.content)
	def _inject_from_remote(B,version,retain=_C):
		C=version;from localstack_ext.bootstrap.pods.utils.remote_utils import extract_meta_and_state_archives as F;D=B._get_presigned_url_for_version_product(version=C);G=D.get(_K);A=new_tmp_file();download(G,A);B.deploy_pod_into_instance(pod_path=A)
		if not retain:rm_rf(A);return _A
		H=D.get(_L);E=new_tmp_file();download(H,E);F(meta_archives={C:E},state_archives={C:A},config_context=B.pods_api.config_context);return _A
	@staticmethod
	def deploy_pod_into_instance(pod_path):
		A=pod_path
		if not A:raise Exception(f"Unable to restore pod state via local pods management API: Pod Path {A} not valid")
		D=_C
		if os.path.isdir(A):
			B=new_tmp_dir()
			for E in PERSISTED_FOLDERS:
				F=os.path.join(A,E)
				if not os.path.exists(F):continue
				H=os.path.join(B,E);cp_r(F,H,rm_dest_on_conflict=_A)
			make_archive(f"{B}.zip",'zip',root_dir=B);rm_rf(B);D=_A
		try:
			I=load_file(A,mode='rb');G=get_pods_endpoint();C=requests.post(G,data=I)
			if C.status_code>=400:raise Exception('Unable to restore pod state via local pods management API %s (code %s): %s'%(G,C.status_code,C.content))
		finally:
			if D:rm_rf(A)
	def inject(A,version=-1,merge=_C):
		C=version
		if not A.pods_api.config_context.pod_exists_locally(A.pod_name):raise Exception(f"Unable to find a local version of pod {A.pod_name}")
		A.pods_api.set_pod_context(A.pod_name)
		if C==-1:C=A.pods_api.get_max_version_no(require_state_archive=_A)
		B=A.pods_api.config_context.get_version_state_archive(C);D=_C
		try:
			if not B and A.pods_api.is_remotely_managed():raise Exception(f"Unable to find a local version of pod {A.pod_name}")
			if not B and C<=Version.DEFAULT_INITIAL_VERSION_NUMBER:B=new_tmp_file();E=A.pods_api.get_state_archive_from_state_files();save_file(B,E);D=_A
			if merge:B=merge_local_state_with(B)
			else:reset_local_state(reset_persistence=_A)
			if not B:raise Exception(f"Unable to find state archive for cloud pod '{A.pod_name}' version {C}")
			A.deploy_pod_into_instance(B);return _A
		finally:
			if D:rm_rf(B)
	def get_version_summaries(A):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.get_version_summaries();return B
	def version_metamodel(A,version):
		B=version;A.pods_api.set_pod_context(A.pod_name)
		if B==-1:B=A.pods_api.get_max_version_no(require_state_archive=_A)
		D=A.pods_api.get_version_by_number(B);E=D.get_latest_revision(with_commit=_A);C=A.pods_api.commit_metamodel_utils.reconstruct_metamodel(version=D,revision=E)
		if not C and A.pods_api.is_remotely_managed():A._download_version_product(version=B,retain=_A);C=A.pods_api.commit_metamodel_utils.create_metamodel_from_state_files(version=B)
		return C
	def set_version(A,version,inject_version_state,reset_state,commit_before):
		B=version;A.pods_api.set_pod_context(A.pod_name);C=A.pods_api.set_active_version(version_no=B,commit_before=commit_before)
		if not C:LOG.warning(f"Could not find version {B}")
		if inject_version_state:A.inject(version=B,merge=_C)
		return C
	def list_version_commits(A,version):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.list_version_commits(version_no=version);C=[A.get_summary()for A in B];return C
	def get_commit_diff(A,version,commit):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.commit_metamodel_utils.get_commit_diff(version_no=version,commit_no=commit);return B
	def register_remote(A,ci_pod=_B):
		A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.get_max_version_no(require_state_archive=_A)
		if B==0:A.pods_api.push('Initial Version');B=1
		F=get_auth_headers();G=A.create_platform_url(A.pod_name);C={_D:A.pod_name,_I:B,'ci_pod':ci_pod};C=json.dumps(C);E=safe_requests.put(G,C,headers=F);H=f"Failed to register pod {A.pod_name}: <content>"
		if not A._check_response(E,message=H):return _C
		D=json.loads(E.content);I={_E:D.get(_E),_J:D.get(_D)};J=D.get(_G);A.pods_api.upload_version_and_product_space(presigned_urls=J);remote_utils.create_remote_info_file(remote_info=I,config_context=A.pods_api.config_context);return _A
	def rename_pod(A,current_pod_name,new_pod_name):
		C=current_pod_name;B=new_pod_name;A.pods_api.set_pod_context(C)
		if B in A.pods_api.list_locally_available_pods():LOG.warning(f"{B} already exists locally");return _C
		if A.pods_api.is_remotely_managed():
			E=get_auth_headers();F=A.create_platform_url(f"{C}/rename");D={'new_pod_name':B};D=json.dumps(D);G=safe_requests.put(F,D,headers=E);H=f"Failed to rename {C} to {B}: <content>"
			if not A._check_response(G,message=H):return _C
		A.pods_api.rename_pod(B);return _A
	def list_pods(A,only_local):
		if only_local:return A.pods_api.list_locally_available_pods(only_local=_A)
		C=A.pods_api.list_locally_available_pods();E=get_auth_headers();F=A.create_platform_url('');D=safe_requests.get(F,headers=E);A._check_response(D,message='Error fetching list of pods from API (status <status_code>)',raise_error=_A);G=json.loads(D.content)
		for B in G or[]:H=B.get(_D)if isinstance(B,dict)else B;C[H].add(PodLocation.REMOTE.value)
		return C
	@classmethod
	def _check_response(C,response,message,raise_error=_C):
		B=response;A=message
		if B.ok:return _A
		if B.status_code in[401,403]:raise Exception('Access denied - please log in first.')
		A=A.replace('<content>',to_str(B.content));A=A.replace('<status_code>',str(B.status_code))
		if raise_error:raise Exception(A)
		LOG.warning(A);return _C
	@staticmethod
	def create_platform_url(path):A=path;B=f"{constants.API_ENDPOINT}/cloudpods";A=A if not A or A.startswith('/')else f"/{A}";return f"{B}{A}"
class PodConfigManagerMeta(type):
	def __getattr__(C,attr):
		def A(*D,**E):
			A=_B
			for F in C.CHAIN:
				try:
					B=getattr(F,attr)(*(D),**E)
					if B:
						if not A:A=B
						elif isinstance(B,list)and isinstance(A,list):A.extend(B)
				except Exception:
					if LOG.isEnabledFor(logging.DEBUG):LOG.exception('error during PodConfigManager call chain')
			if A is not _B:return A
			raise Exception('Unable to run operation "%s" for local or remote configuration'%attr)
		return A
class PodConfigManager(metaclass=PodConfigManagerMeta):
	CHAIN=[]
	@classmethod
	def pod_config(D,pod_name):
		A=pod_name;C=PodConfigManager.list_pods();B=[B for B in C if B[_D]==A]
		if not B:raise Exception('Unable to find config for pod named "%s"'%A)
		return B[0]
def get_pods_manager(pods_name):return CloudPodsVersionManager(pod_name=pods_name)
def init_cloudpods(pod_name,**B):A=get_pods_manager(pods_name=pod_name);A.init()
def delete_pod(pod_name,remote):A=get_pods_manager(pods_name=pod_name);B=A.delete(remote=remote);return B
def register_remote(pod_name,ci_pod=_B,**C):A=get_pods_manager(pods_name=pod_name);B=A.register_remote(ci_pod=ci_pod);return B
def rename_pod(current_pod_name,new_pod_name,**D):A=new_pod_name;B=get_pods_manager(pods_name=A);C=B.rename_pod(current_pod_name=current_pod_name,new_pod_name=A);return C
def list_pods(local,**C):A=get_pods_manager(pods_name='');B=A.list_pods(only_local=local);return B
def commit_state(pod_name,message=_B,services=_B,**C):
	B=pod_name;A=get_pods_manager(pods_name=B)
	if not A.pods_api.config_context.is_initialized():A.init()
	A.pods_api.set_pod_context(pod_name=B);A.commit(message=message,services=services)
def inject_state(pod_name,version,merge,**C):A=get_pods_manager(pods_name=pod_name);B=A.inject(version=version,merge=merge);return B
def get_version_summaries(pod_name):B=get_pods_manager(pods_name=pod_name);A=B.get_version_summaries();A=A[::-1];return A
def get_version_metamodel(version,pod_name,**C):A=get_pods_manager(pods_name=pod_name);B=A.version_metamodel(version=version);return B
def set_version(version,inject_version_state,reset_state,commit_before,pod_name,**C):A=get_pods_manager(pods_name=pod_name);B=A.set_version(version=version,inject_version_state=inject_version_state,reset_state=reset_state,commit_before=commit_before);return B
def list_version_commits(version,pod_name):A=get_pods_manager(pods_name=pod_name);B=A.list_version_commits(version=version);return B
def get_commit_diff(version,commit,pod_name):A=get_pods_manager(pods_name=pod_name);B=A.get_commit_diff(version=version,commit=commit);return B
def push_overwrite(version,pod_name,comment,services=_B):A=get_pods_manager(pods_name=pod_name);A.push_overwrite(version=version,comment=comment,services=services)
def push_state(pod_name,comment=_B,register=_C,services=_B,**E):
	C=pod_name;B=services
	if B is _B:B=[]
	A=get_pods_manager(pods_name=C)
	if not A.pods_api.config_context.is_initialized():A.init()
	A.pods_api.set_pod_context(pod_name=C);A.push(comment=comment,services=B);D=_A
	if register:D&=A.register_remote()
	return D
def get_pods_endpoint():A=config.get_edge_url();return f"{A}{API_PATH_PODS}"
def pull_state(pod_name,inject=_A,merge=_C,**C):
	A=pod_name
	if not A:raise Exception('Need to specify a pod name')
	B=get_pods_manager(pods_name=A);B.pull(inject=inject,merge=merge);print('Done.')
def reset_local_state(reset_persistence=_C,services=_B):
	E=services;D=reset_persistence;C=f"{get_pods_endpoint()}/state/reset";A={}
	if D:A['persistence']=D
	if E:A[_F]=','.join(E)
	LOG.debug('Sending request to reset the service states in local instance with params %s',A)
	if A:B=requests.delete(C,params=A)
	else:B=requests.delete(C)
	if B.status_code>=400:raise Exception('Unable to reset service state via local management API %s (code %s): %s'%(C,B.status_code,B.content))
	print('Done.')
def merge_local_state_with(state_archive_path):from localstack_ext.bootstrap.pods.servicestate.utils import handle_get_state_request_in_memory as C;D=C();A=ServiceStateMarshaller.unmarshall(D.data);E=ServiceStateMarshaller.unmarshall_zip_archive(state_archive_path);A.merge(E,_B);B=new_tmp_file();ServiceStateMarshaller.marshall_zip_archive(B,A);return B
def save_pods_config(options):A=get_pods_manager('');A.pods_api.config_context.save_pods_config(options=options)
def get_pod_name_from_config():A=get_pods_manager('');return A.pods_api.config_context.get_pod_name_from_config()
def is_initialized(pod_name):A=get_pods_manager(pods_name=pod_name);return A.pods_api.config_context.is_initialized()
def get_data_dir_from_container():
	try:
		C=DOCKER_CLIENT.inspect_container(config.MAIN_CONTAINER_NAME);D=C.get('Mounts');E=C.get('Config',{}).get('Env',[]);A=[A for A in E if A.startswith('DATA_DIR=')][0].partition('=')[2]
		try:B=[B for B in D if B['Destination']==A][0]['Source'];B=re.sub('^(/host_mnt)?','',B);A=B
		except Exception:LOG.debug(f"No docker volume for data dir '{A}' detected")
		return A
	except Exception:LOG.warning('Unable to determine DATA_DIR from LocalStack Docker container - please make sure $MAIN_CONTAINER_NAME is configured properly')
def get_persisted_resource_names(data_dir):
	D=data_dir;B=[]
	with os.scandir(D)as C:
		for A in C:
			if A.is_dir()and A.name!=_H:B.append(A.name)
	with os.scandir(os.path.join(D,_H))as C:
		for A in C:
			if A.is_dir()and len(os.listdir(A.path))>0:B.append(A.name)
	LOG.debug(f"Detected state files for the following APIs: {B}");return B
PODS_NAMESPACE_DELIM='-'