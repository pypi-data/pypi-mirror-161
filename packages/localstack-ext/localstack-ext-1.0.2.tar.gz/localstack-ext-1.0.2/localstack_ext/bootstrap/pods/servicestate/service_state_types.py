from typing import TYPE_CHECKING,Dict,NamedTuple,Union
if TYPE_CHECKING:from localstack.services.generic_proxy import RegionBackend;from moto.core.utils import BackendDict
BackendType=Union['RegionBackend','BackendDict',bytes]
Backends=Dict[str,BackendType]
ServiceNameType=str
AssetNameType=str
Blob=bytes
AssetValueType=Blob
AssetByNameType=Dict[AssetNameType,AssetValueType]
AssetByServiceType=Dict[ServiceNameType,AssetByNameType]
class AccountRegion(NamedTuple):account_id:str;region:str
class ServiceKey(NamedTuple):
	account_id:str;region:str;service:str
	@staticmethod
	def for_region_and_service(region,service):A=region;return ServiceKey(account_id=A.account_id,region=A.region,service=service)
class BackendState:
	key:0;backends:0
	def __init__(A,key,backends):A.key=key;A.backends=backends