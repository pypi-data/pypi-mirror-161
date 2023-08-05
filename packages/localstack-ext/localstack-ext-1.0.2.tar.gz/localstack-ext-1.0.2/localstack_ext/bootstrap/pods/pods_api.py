_D='rb'
_C=True
_B=False
_A=None
import hashlib,json,logging,os,zipfile
from collections import defaultdict
from typing import Any,Dict,List,Optional,Set,Tuple
from localstack.aws.accounts import get_aws_account_id
from localstack.utils.common import cp_r,mkdir,rm_rf,save_file,short_uid,to_str
from localstack.utils.files import load_file
from localstack.utils.http import safe_requests
from localstack_ext.bootstrap.licensing import ENV_LOCALSTACK_API_KEY,api_key_configured
from localstack_ext.bootstrap.pods.constants import NIL_PTR,VERSION_SPACE_ARCHIVE
from localstack_ext.bootstrap.pods.models import Commit,Revision,Serialization,StateFileRef,Version
from localstack_ext.bootstrap.pods.object_storage import get_object_storage_provider
from localstack_ext.bootstrap.pods.servicestate.service_state import ServiceState
from localstack_ext.bootstrap.pods.servicestate.service_state_types import BackendState,ServiceKey
from localstack_ext.bootstrap.pods.utils.adapters import ServiceStateMarshaller
from localstack_ext.bootstrap.pods.utils.common import PodsConfigContext,marshall_backend,unmarshall_backend,zip_directories
from localstack_ext.bootstrap.pods.utils.hash_utils import compute_file_hash,compute_revision_hash,random_hash
from localstack_ext.bootstrap.pods.utils.metamodel_utils import CommitMetamodelUtils
from localstack_ext.bootstrap.pods.utils.remote_utils import extract_meta_and_state_archives,merge_version_space
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR
LOG=logging.getLogger(__name__)
ROOT_DIR_LOOKUP={str(Serialization.KINESIS):KINESIS_DIR,str(Serialization.DDB):DYNAMODB_DIR,str(Serialization.MAIN):API_STATES_DIR}
class PodsApi:
	def __init__(A,config_context):A.config_context=config_context;A.object_storage=get_object_storage_provider(A.config_context);A.commit_metamodel_utils=CommitMetamodelUtils(A.config_context)
	def init(A,pod_name=_A):
		C=pod_name;C=C or A.config_context.pod_name
		if A.config_context.pod_exists_locally(pod_name=C):LOG.warning(f"Pod with name {C} already exists locally");return
		mkdir(A.config_context.get_pod_root_dir());mkdir(A.config_context.get_versions_path());mkdir(A.config_context.get_obj_store_path());save_file(A.config_context.get_known_ver_path(),'');A.config_context.set_pod_context(C);F=random_hash();G=random_hash();E=Revision(hash_ref=F,parent_ptr=NIL_PTR,creator=A.config_context.get_context_user(),rid=short_uid(),revision_number=0,state_files=set());B=Version(hash_ref=G,parent_ptr=NIL_PTR,creator=A.config_context.get_context_user(),comment='Initial version',outgoing_revision_ptrs={F},incoming_revision_ptr=_A,state_files=set(),version_number=Version.DEFAULT_INITIAL_VERSION_NUMBER);B.revisions.append(E);A.object_storage.upsert_objects(B)
		with open(A.config_context.get_head_path(),'w')as D:D.write(str(B.version_number))
		with open(A.config_context.get_max_ver_path(),'w')as D:D.write(str(B.version_number))
		with open(A.config_context.get_known_ver_path(),'w')as D:D.write(str(B.version_number))
		A.config_context.update_ver_log(author=A.config_context.get_context_user(),ver_no=B.version_number,rev_id=E.rid,rev_no=E.revision_number);LOG.debug('Successfully initialized cloud pod under %s',A.config_context.get_pod_root_dir())
	def commit(D,message=_A):
		A,B=D._get_expansion_point_with_head();E=compute_revision_hash(A,D.config_context.get_obj_store_path())
		if A.parent_ptr!=NIL_PTR:F=B.get_revision(A.parent_ptr);F.assoc_commit.head_ptr=E
		B.update_revision_key(old_key=A.hash_ref,new_key=E);A.hash_ref=E;C=Revision(hash_ref=random_hash(),state_files=set(),parent_ptr=E,creator=A.creator,rid=short_uid(),revision_number=A.revision_number+1);B.revisions.append(C);G=Commit(tail_ptr=A.hash_ref,head_ptr=C.hash_ref,message=message);A.assoc_commit=G;D.object_storage.upsert_objects(B);D.config_context.update_ver_log(author=C.creator,ver_no=B.version_number,rev_id=C.rid,rev_no=C.revision_number);return A
	def merge_from_remote(A,version_space_archive,meta_archives,state_archives):merge_version_space(version_space_archive,config_context=A.config_context);extract_meta_and_state_archives(meta_archives=meta_archives,state_archives=state_archives,config_context=A.config_context)
	def is_remotely_managed(A):return A.config_context.is_remotely_managed()
	def rename_pod(B,new_pod_name):
		A=new_pod_name
		if B.config_context.pod_exists_locally(A):LOG.warning(f"{A} already exists locally");return _B
		B.config_context.rename_pod(A);return _C
	def list_locally_available_pods(A,only_local=_B):
		from localstack_ext.bootstrap.pods_client import PodLocation as B;mkdir(A.config_context.cloud_pods_root_dir);C=[B for B in os.listdir(A.config_context.cloud_pods_root_dir)if not B.endswith('.json')]
		if only_local:return{A:{'local'}for A in C}
		D=defaultdict(set)
		for E in C:F=A.config_context.is_remotely_managed(E);D[E].add(B.REMOTE.value if F else B.LOCAL.value)
		return D
	def push(A,comment=_A):
		B,D=A._get_expansion_point_with_head();I=A._get_max_version();F=D.version_number;G=I.version_number;K=G+1;J=F!=G;H=A._create_service_state_from_state_file_refs(state_file_refs=B.state_files,unmarshall_backends=J)
		if J:
			if not api_key_configured():LOG.warning(f"Please note that you'll need to set {ENV_LOCALSTACK_API_KEY} to perform push/merge operations")
			A.merge_expansion_point_with_max(H);F=G
		L=A.config_context.get_version_state_archive_path(F);ServiceStateMarshaller.marshall_zip_archive(file_path=L,service_state=H);D.hash_ref=H.compute_hash_on_state();E=Revision(hash_ref=random_hash(),state_files=B.state_files,parent_ptr=NIL_PTR,creator=B.creator,rid=short_uid(),revision_number=0);C=Version(hash_ref=random_hash(),state_files=set(),parent_ptr=I.hash_ref,creator=B.creator,comment=comment,outgoing_revision_ptrs={E.hash_ref},incoming_revision_ptr=B.hash_ref,version_number=K);C.revisions.append(E);M=Commit(tail_ptr=B.hash_ref,head_ptr=C.hash_ref,message='Finalizing commit');B.state_files=C.state_files;B.assoc_commit=M;A.object_storage.upsert_objects(D,C);A._update_head(C.version_number);A._update_max_ver(C.version_number);A._add_known_ver(C.version_number);N=A.config_context.metamodel_file(B.revision_number);A.commit_metamodel_utils.create_metamodel_archive(D,overwrite=_C,metamodels_file=N);A.config_context.update_ver_log(author=B.creator,ver_no=C.version_number,rev_id=E.rid,rev_no=E.revision_number);return C
	def set_pod_context(A,pod_name):A.config_context.set_pod_context(pod_name)
	def add_metamodel_to_current_revision(A,metamodel):B,C=A._get_expansion_point_with_head();D=json.dumps(metamodel);E=A._create_state_file_from_blob(D);B.metamodel_file=E;A.object_storage.upsert_objects(C)
	def get_revision_metamodel(C,revision=_A):
		A=revision
		if not A:A,E=C._get_expansion_point_with_head()
		if not A.metamodel_file:return{}
		D=C.config_context.get_obj_file_path(A.metamodel_file);B=load_file(D);B=json.loads(to_str(B));return B
	def create_state_file_from_fs(C,file_name,service,region,root,serialization=Serialization.MAIN,account_id=_A,object=_A,rel_path=_A):
		E=region;D=service;A=account_id
		if A is _A:A=get_aws_account_id()
		B=hashlib.sha1(object).hexdigest();F=C.config_context.get_obj_file_path(B);save_file(file=F,content=object);G=StateFileRef(hash_ref=B,rel_path=rel_path or f"{root}/{A}/{D}/{E}",file_name=file_name,size=len(object),service=D,region=E,account_id=A,serialization=serialization);C._add_state_file_to_expansion_point(G);return B
	def _create_state_file_from_blob(C,blob):
		A=blob;E=random_hash();B=C.config_context.get_obj_file_path(E)
		if not isinstance(A,(str,bytes)):A=marshall_backend(A)
		save_file(B,A);D=compute_file_hash(B);F=C.config_context.get_obj_file_path(D);os.rename(B,F);return D
	def _get_state_file_path(B,key):
		A=B.config_context.get_obj_file_path(key)
		if os.path.isfile(A):return A
		LOG.warning(f"No state file with found with key: {key}")
	def _add_state_file_to_expansion_point(A,state_file):B=state_file;C,E=A._get_expansion_point_with_head();D=set(filter(lambda sf:not sf.congruent(B),C.state_files));D.add(B);C.state_files=D;A.object_storage.upsert_objects(E)
	def create_version_space_archive(A):
		B=os.path.join(A.config_context.get_pod_root_dir(),VERSION_SPACE_ARCHIVE);rm_rf(B);C=zip_directories(zip_dest=B,directories=A.config_context.get_version_space_dir_paths())
		with zipfile.ZipFile(C,'a')as E:
			for D in A.config_context.get_version_space_file_paths():E.write(D,arcname=os.path.basename(D))
		return C
	def get_head(A):return A.object_storage.get_version(A.config_context.get_head_version_number())
	def _get_max_version(A):return A.object_storage.get_version(A.config_context.get_max_version_number())
	def get_max_version_no(B,require_state_archive=_B):
		C=load_file(B.config_context.get_max_ver_path());A=int(os.path.basename(C))
		if require_state_archive:
			D=reversed(list(range(1,A+1)))
			for A in D:
				E=B.config_context.get_version_state_archive(A)
				if E:break
		return A
	def _get_expansion_point_with_head(B):A=B.get_head();C=A.get_latest_revision();return C,A
	def get_state_archive_from_state_files(B,version=_A):
		A=version
		if not A:F,A=B._get_expansion_point_with_head()
		C=ServiceState()
		for D in A.revisions_with_commit:E=B._create_service_state_from_state_file_refs(state_file_refs=D.state_files,unmarshall_backends=_B);C.put_service_state(E)
		return ServiceStateMarshaller.marshall(state=C)
	def push_overwrite(A,version,comment):
		B=version;D,H=A._get_expansion_point_with_head()
		if B>A.get_max_version_no():LOG.debug('Attempted to overwrite a non existing version.. Aborting');return _B
		C=A.get_version_by_number(B);E=A._create_service_state_from_state_file_refs(state_file_refs=D.state_files);F=A.config_context.get_version_state_archive_path(B);ServiceStateMarshaller.marshall_zip_archive(file_path=F,service_state=E);G=A.config_context.metamodel_file(D.revision_number);A.commit_metamodel_utils.create_metamodel_archive(C,overwrite=_C,metamodels_file=G);C.comment=comment;A.object_storage.upsert_objects(C);return _C
	def _add_assets_to_version_state_archive(A,version_number,cleanup=_C):
		D=A.config_context.get_version_state_archive_path(version=version_number);B=A.config_context.get_assets_root_path()
		with zipfile.ZipFile(D,'a')as E:
			for (F,I,G) in os.walk(B):
				for H in G:C=os.path.join(F,H);E.write(filename=C,arcname=os.path.relpath(C,start=A.config_context.get_pod_root_dir()))
		if cleanup:rm_rf(B)
	@staticmethod
	def _get_dst_path_for_state_file(version_state_dir,state_file):
		C=version_state_dir;A=state_file
		if A.serialization in[str(Serialization.KINESIS),str(Serialization.DDB)]:B=os.path.join(C,ROOT_DIR_LOOKUP[str(A.serialization)])
		else:B=os.path.join(C,ROOT_DIR_LOOKUP[str(A.serialization)],A.rel_path)
		mkdir(B);return B
	def _create_service_state_from_state_file_refs(C,state_file_refs,unmarshall_backends=_B):
		A=ServiceState()
		for B in state_file_refs:
			D=B.rel_path.startswith('api_states')
			if D:E=C._create_backend_state_from_state_file(B,unmarshall=unmarshall_backends);A.put_backend(E)
			else:C._add_assets_from_state_file(B,A)
		return A
	def _create_backend_state_from_state_file(C,state_file,unmarshall):
		A=state_file;D=ServiceKey(account_id=A.account_id,region=A.region,service=A.service);E=C.object_storage.get_state_file_location_by_key(A.hash_ref);B=load_file(file_path=E,mode=_D)
		if unmarshall:B=unmarshall_backend(B)
		return BackendState(key=D,backends={A.file_name:B})
	def _add_assets_from_state_file(B,state_file,service_state):A=state_file;C=B.object_storage.get_state_file_location_by_key(A.hash_ref);D=load_file(file_path=C,mode=_D);service_state.put_asset(service_name=A.service,asset_name=A.rel_path,asset_value=D)
	def set_active_version(A,version_no,commit_before=_B):
		B=version_no;C=A.config_context.list_known_versions()
		for D in C:
			if D==B:
				if commit_before:A.commit()
				A._set_active_version(B);return _C
		LOG.info(f"Version with number {B} not found");return _B
	def _set_active_version(A,version_no):
		C=version_no;D=A.get_head()
		if D.version_number!=C and A.object_storage.version_exists(D.version_number):
			B=A.object_storage.get_version(C);A._update_head(B.version_number)
			if B.active_revision_ptr==NIL_PTR:E=Revision(hash_ref=random_hash(),state_files=set(),parent_ptr=NIL_PTR,creator=A.config_context.get_context_user(),rid=short_uid(),revision_number=0);B.revisions.append(E);B.outgoing_revision_ptrs.add(E.hash_ref);A.object_storage.upsert_objects(B)
	def get_version_by_number(B,version_no):
		A=version_no;C=B.config_context.list_known_versions()
		if A not in C:LOG.warning('Could not find version number %s',A);return
		return B.object_storage.get_version(A)
	def list_versions(A):B=A.config_context.list_known_versions();C=[A.object_storage.get_version(C)for C in B];return C
	def get_version_summaries(A):
		def B(version):A=version;return f"{A.version_number}, {A.creator}, {A.comment}"
		C=A.list_versions();D=[B(A)for A in C];return D
	def list_version_commits(C,version_no):
		D=version_no
		if D==-1:A=C._get_max_version()
		else:A=C.get_version_by_number(D)
		if not A:return[]
		E=[];B=A.get_revision(A.incoming_revision_ptr)
		if not B:B=A.revisions[0]
		while B:
			F=B.assoc_commit
			if F:E.append(F)
			B=A.get_revision(B.parent_ptr)
		return E
	def _update_head(B,new_head_ver_no):
		A=new_head_ver_no
		with open(B.config_context.get_head_path(),'w')as C:C.write(str(A));return str(A)
	def _update_max_ver(B,new_max_ver_no):
		A=new_max_ver_no
		with open(B.config_context.get_max_ver_path(),'w')as C:C.write(str(A));return str(A)
	def _add_known_ver(B,new_ver_no):
		A=new_ver_no
		with open(B.config_context.get_known_ver_path(),'a')as C:C.write(f"\n{A}");return str(A)
	def merge_expansion_point_with_max(A,current):
		C=current;F=A.get_max_version_no(require_state_archive=_C);D=A.get_head().version_number;LOG.debug('Merge expansion point with max. Services in the new version service state = %s',C.get_services());G=A.config_context.get_version_state_archive(F);E=ServiceStateMarshaller.unmarshall(zipfile.ZipFile(G));LOG.debug('Merge expansion point with max. Services in the max service state = %s',E.get_services());B=_A
		if D>Version.DEFAULT_INITIAL_VERSION_NUMBER:H=A.config_context.get_version_state_archive(D);B=ServiceStateMarshaller.unmarshall(zipfile.ZipFile(H));LOG.debug('Merge expansion point with max. Services in the ancestor service state = %s',B.get_services())
		C.merge(E,B)
	def add_assets_to_pod(B,assets_root_paths):
		for A in assets_root_paths:
			C=os.path.join(B.config_context.get_assets_root_path(),os.path.basename(A))
			try:cp_r(src=A,dst=C)
			except Exception as D:LOG.warning('Failed to copy assets for %s: %s',A,D)
	def upload_version_and_product_space(A,presigned_urls):
		C=presigned_urls
		def B(pre_signed_url,zip_data_content):
			A=safe_requests.put(pre_signed_url,data=zip_data_content)
			if A.status_code>=400:raise Exception(f"Unable to upload pod state to S3 (code {A.status_code}): {A.content}")
			return A
		I=C.get('version_space_url');D=A.create_version_space_archive()
		with open(D,_D)as J:B(I,J.read())
		K=C.get('meta_state_urls');rm_rf(D)
		for (E,F) in K.items():
			L=F['meta'];G=A.config_context.get_version_meta_archive(E)
			if G:M=load_file(G,mode=_D);B(L,M)
			N=F['state'];H=A.config_context.get_version_state_archive(E)
			if H:O=load_file(H,mode=_D);B(N,O)