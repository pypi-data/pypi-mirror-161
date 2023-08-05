import logging
from typing import Callable,Optional
from localstack_ext.bootstrap.pods.servicestate.service_state_types import AssetByNameType
from localstack_ext.bootstrap.state_merge_ddb import merge_dynamodb
from localstack_ext.bootstrap.state_merge_kinesis import merge_kinesis
LOG=logging.getLogger(__name__)
def get_merge_function_for_assets(service):
	match service:
		case'dynamodb':return merge_dynamodb
		case'kinesis':return merge_kinesis
		case _:return override_default_merge
def override_default_merge(current,inject,ancestor):A=current;LOG.debug('No merge function specified for the service: replacing the application state with the injecting one.');A.clear();A.update(inject)