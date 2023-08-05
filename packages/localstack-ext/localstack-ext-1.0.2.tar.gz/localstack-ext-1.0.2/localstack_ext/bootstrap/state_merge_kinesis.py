import json,logging
from typing import Optional,Set
from localstack_ext.bootstrap.pods.servicestate.service_state_types import AssetByNameType,AssetValueType
from localstack_ext.bootstrap.state_merge import merge_object_state
LOG=logging.getLogger(__name__)
def merge_kinesis(current,inject,ancestor):
	O=b'{}';I=None;F='utf-8';E=inject;C=ancestor;B=current;P={*B.keys(),*E.keys(),*(C.keys()if C else{})}
	for A in P:
		J=A in B;K=A in E;L=A in C if C else False;Q=not J and K and not L;R=J and not K and L;S=A=='kinesis-data.json'
		if Q:B[A]=E[A]
		elif R:del B[A]
		else:
			D=B.get(A,O);G=E.get(A,O);H=C.get(A,I)if C else I
			if S:M=json.loads(D.decode(F));T=json.loads(G.decode(F));U=json.loads(H.decode(F))if H else I;merge_object_state(M,T,U);D=AssetValueType(json.dumps(M),F);B[A]=D
			else:
				N='no strict injecting update hence accepting current version.';V=D==H and D!=G
				if V:B[A]=G;N='strict injecting update hence accepting injecting version.'
				LOG.warning(f"No handling routine for merging of kinesis asset '{A}': {N}")