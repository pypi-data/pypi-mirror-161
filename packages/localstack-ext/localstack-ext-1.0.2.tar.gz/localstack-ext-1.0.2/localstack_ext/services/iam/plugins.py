from localstack.runtime import hooks
from localstack_ext import config as config_ext
from localstack_ext.plugins import api_key_configured
@hooks.on_infra_start(should_load=lambda:api_key_configured()and config_ext.LEGACY_IAM_ENFORCEMENT)
def add_legacy_iam_enforcement_listener():from localstack.aws.handlers import serve_custom_service_request_handlers as A;from localstack_ext.services.iam.legacy_handler import LegacyIamEnforcementHandler as B;A.handlers.append(B())
@hooks.on_infra_start(should_load=lambda:api_key_configured()and not config_ext.LEGACY_IAM_ENFORCEMENT)
def add_iam_enforcement_listener():from localstack.aws.handlers import serve_custom_service_request_handlers as A;from localstack_ext.services.iam.policy_engine.handler import IamEnforcementHandler as B;A.handlers.append(B())