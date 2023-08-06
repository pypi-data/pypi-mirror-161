from localstack.runtime import hooks
from localstack_ext.plugins import api_key_configured
EXTENSION_HOOK_PRIORITY=-1
@hooks.on_infra_start(priority=EXTENSION_HOOK_PRIORITY,should_load=api_key_configured)
def extensions_on_infra_start():from localstack_ext.extensions.platform import run_on_infra_start_hook as A;A()
@hooks.on_infra_ready(priority=EXTENSION_HOOK_PRIORITY,should_load=api_key_configured)
def extensions_on_infra_ready():from localstack_ext.extensions.platform import run_on_infra_ready_hook as A;A()