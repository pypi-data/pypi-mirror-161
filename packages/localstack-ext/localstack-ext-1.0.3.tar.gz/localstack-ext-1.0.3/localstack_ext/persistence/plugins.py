from localstack.runtime import hooks
from localstack_ext.plugins import api_key_configured
@hooks.on_infra_start(should_load=api_key_configured)
def register_pods_api():from localstack.services.edge import ROUTER as A;from localstack_ext.persistence.pods_api import PodsApi as B;A.add_route_endpoints(B())
@hooks.on_infra_start(should_load=api_key_configured)
def register_state_serializer_handlers():from localstack.aws.handlers import run_custom_response_handlers as A,serve_custom_service_request_handlers as B;from localstack_ext.persistence.handlers import CIMetricPublisher as C,PodStateSyncHandler as D,StateSerializerHandler as E;B.handlers.append(D());A.handlers.append(E());A.handlers.append(C())