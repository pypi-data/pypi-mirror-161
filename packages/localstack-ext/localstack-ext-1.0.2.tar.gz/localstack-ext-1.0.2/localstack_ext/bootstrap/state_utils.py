_A='__dict__'
import logging,os
from typing import Any,Callable,List,OrderedDict,Set,Tuple
from localstack.utils.common import ObjectIdHashComparator
from localstack.utils.files import rm_rf
API_STATES_DIR='api_states'
KINESIS_DIR='kinesis'
DYNAMODB_DIR='dynamodb'
POD_KEEP='.podkeep'
LOG=logging.getLogger(__name__)
def check_already_visited(obj,visited):
	A=visited
	if hasattr(obj,_A):
		A=A or set();B=ObjectIdHashComparator(obj)
		if B in A:return True,A
		A.add(B)
	return False,A
def check_already_visited_obj_id(obj,visited):A=visited;A=A or set();B=id(obj);C=B in A;A.add(B);return C,A
def get_object_dict(obj):
	A=obj
	if isinstance(A,dict):return A
	B=getattr(A,_A,None);return B
def is_composite_type(obj):return isinstance(obj,(dict,OrderedDict,list,set))or hasattr(obj,_A)
def api_states_traverse(api_states_path,side_effect,mutables):
	B=side_effect
	for (A,K,E) in os.walk(api_states_path):
		for C in E:
			try:F=os.path.normpath(A).split(os.sep);G,H,I=F[-3:];B(dir_name=A,fname=C,region=I,service_name=H,account_id=G,mutables=mutables)
			except Exception as J:
				D=f"Failed to apply {B.__name__} for {C} in dir {A}: {J}";LOG.warning(D)
				if LOG.isEnabledFor(logging.DEBUG):LOG.exception(D)
				continue
def cleanse_keep_files(file_path):
	for (B,D,C) in os.walk(file_path):
		for A in C:
			if A==POD_KEEP:rm_rf(os.path.join(B,A))
def populate_empty_dirs(file_path):
	for (B,C,G) in os.walk(file_path):
		for D in C:
			A=os.path.join(B,D);E=list((B for B in os.listdir(A)if os.path.isfile(os.path.join(A,B))))
			if not E:
				F=os.path.join(A,POD_KEEP)
				with open(F,'w'):0