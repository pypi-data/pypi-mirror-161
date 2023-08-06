import io,logging,os,zipfile
from typing import Any,Callable,List
from localstack.utils.files import load_file,save_file
from localstack_ext.bootstrap.pods.service_state.service_state import ServiceState
from localstack_ext.bootstrap.pods.service_state.service_state_types import AssetNameType,AssetValueType,BackendState,BackendType,ServiceKey,ServiceNameType
LOG=logging.getLogger(__name__)
class ServiceStateMarshaller:
	@staticmethod
	def marshall(state,marshall_function=None):
		F=marshall_function;E=state;B=io.BytesIO()
		with zipfile.ZipFile(B,'a')as G:
			for (C,J) in E.state.items():
				K=os.path.join(C.account_id,C.service,C.region)
				for (L,A) in J.backends.items():
					if not isinstance(A,bytes)and F:A=F(A)
					G.writestr(os.path.join('api_states',K,L),A)
			for (H,M) in E.assets.items():
				for (I,D) in M.items():
					if D is None:continue
					try:N=os.path.join(H,I);G.writestr(N,D)
					except Exception as O:LOG.exception('Failed to marshall %s for %s with value %s: %s',I,H,D,O)
		B.seek(0);return B.getvalue()
	@staticmethod
	def unmarshall(zip_content,raw_bytes=False,unmarshall_function=None):
		E=unmarshall_function;D=raw_bytes;A=zip_content
		if not A:return ServiceState()
		if not D and not E:LOG.debug('No unmarshal function provided')
		if isinstance(A,bytes):
			try:A=zipfile.ZipFile(io.BytesIO(A))
			except Exception as F:LOG.debug(f"Zip content not valid: {F}")
		C=ServiceState()
		def G(_filename):
			F=_filename;G=F.split(os.sep);H,I,J,K=G[-4:];B=A.read(F)
			if not D:B=E(B)
			L=BackendState(key=ServiceKey(H,J,I),backends={K:B});C.put_backend(L)
		def H(_filename):B=_filename;D=os.path.normpath(B).split(os.sep);E=D[0];F=os.path.join(*D[1:]);G=A.read(B);C.put_asset(E,F,G)
		for B in A.namelist():
			if not B.endswith('/'):
				if B.startswith('api_'):G(_filename=B)
				else:H(_filename=B)
		return C
	@staticmethod
	def unmarshall_zip_archive(file_path):A=load_file(file_path,mode='rb');return ServiceStateMarshaller.unmarshall(A,raw_bytes=True)
	@staticmethod
	def marshall_zip_archive(file_path,service_state):
		A=service_state
		try:B=ServiceStateMarshaller.marshall(state=A)
		except Exception as C:LOG.exception('Failing to marshall service state: %s. Using original state',C);B=A
		save_file(file_path,B)