import io,logging,os,zipfile
from typing import List
from localstack.utils.files import load_file,save_file
from localstack_ext.bootstrap.pods.servicestate.service_state import ServiceState
from localstack_ext.bootstrap.pods.servicestate.service_state_types import AssetNameType,AssetValueType,BackendState,BackendType,ServiceKey,ServiceNameType
from localstack_ext.bootstrap.pods.utils.common import marshall_backend,unmarshall_backend
LOG=logging.getLogger(__name__)
class ServiceStateMarshaller:
	@staticmethod
	def marshall(state):
		D=state;A=io.BytesIO()
		with zipfile.ZipFile(A,'a')as E:
			for (B,H) in D.state.items():
				I=os.path.join(B.account_id,B.service,B.region)
				for (J,K) in H.backends.items():L=marshall_backend(K);E.writestr(os.path.join('api_states',I,J),L)
			for (F,M) in D.assets.items():
				for (G,C) in M.items():
					if C is None:continue
					try:N=os.path.join(F,G);E.writestr(N,C)
					except Exception as O:LOG.exception('Failed to marshall %s for %s with value %s: %s',G,F,C,O)
		A.seek(0);return A.getvalue()
	@staticmethod
	def unmarshall(zip_content,raw_bytes=False):
		A=zip_content
		if isinstance(A,bytes):A=zipfile.ZipFile(io.BytesIO(A))
		C=ServiceState()
		def D(_filename):
			D=_filename;E=D.split('/');F,G,H,I=E[-4:];B=A.read(D)
			if not raw_bytes:B=unmarshall_backend(B)
			J=BackendState(key=ServiceKey(F,H,G),backends={I:B});C.put_backend(J)
		def E(_filename):B=_filename;D=os.path.normpath(B).split(os.sep);E=D[0];F=os.path.join(*D[1:]);G=A.read(B);C.put_asset(E,F,G)
		for B in A.namelist():
			if not B.endswith('/'):
				if B.startswith('api_'):D(_filename=B)
				else:E(_filename=B)
		return C
	@staticmethod
	def unmarshall_zip_archive(file_path):A=load_file(file_path,mode='rb');return ServiceStateMarshaller.unmarshall(A)
	@staticmethod
	def marshall_zip_archive(file_path,service_state):
		A=service_state
		try:B=ServiceStateMarshaller.marshall(state=A)
		except Exception as C:LOG.exception('Failing to marshall service state: %s. Using original state',C);B=A
		save_file(file_path,B)