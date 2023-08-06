"""
some api class names have chaged in Swagger
so reference names for modules are different
import these classes with the old name to support users
that may have implemented the API's with the old names

"""
#from assetic.apis import AssetApi as ComplexAssetApi
##Data exchange Job
from assetic.models.assetic3_integration_representations_data_exchange_job_representation \
     import Assetic3IntegrationRepresentationsDataExchangeJobRepresentation \
     as Assetic3WebApiModelsDataExchangeDataExchangeJobVM
     
from ..api import AssetApi
from ..api import WorkOrderApi
from ..api_client import ApiClient
from ..api import WorkRequestApi

# WorkRequestApi.work_request_get = \
#     WorkRequestApi.work_request_integration_api_get
# WorkRequestApi.work_request_get_0 = \
#     WorkRequestApi.work_request_integration_api_get_0
# WorkRequestApi.work_request_post = \
#     WorkRequestApi.work_request_integration_api_post
# WorkRequestApi.work_request_put = \
#     WorkRequestApi.work_request_integration_api_put
# WorkRequestApi.work_request_add_supporting_information_for_work_request = \
#     WorkRequestApi.work_request_integration_api_add_supporting_information_for_work_request
# WorkRequestApi.work_request_get_supporting_information_for_work_request = \
#     WorkRequestApi.work_request_integration_api_get_supporting_information_for_work_request
# WorkRequestApi.work_request_get_work_request_type = \
#     WorkRequestApi.work_request_integration_api_get_work_request_type


class ComplexAssetApi(object):
    """
    Class to alias AssetApi (new name)
    Allows backward compatibility for existing scripts
    Use AssetApi
    """
    def __init__(self, api_client=None):
        self._assetapi = AssetApi(api_client)
        self.complex_asset_get = self._assetapi.asset_get
        self.complex_asset_get_with_http_info = self._assetapi.asset_get_with_http_info
        self.complex_asset_get_0 = self._assetapi.asset_get_0
        self.complex_asset_get_0_with_http_info = self._assetapi.asset_get_0_with_http_info
        self.complex_asset_post = self._assetapi.asset_post
        self.complex_asset_post_with_http_info = self._assetapi.asset_post_with_http_info
        self.complex_asset_put = self._assetapi.asset_put
        self.complex_asset_put_with_http_info = self._assetapi.asset_put_with_http_info


class WorkOrderIntegrationApiApi(object):
    """
    Class to alias WorkOrderApi (new name)
    Allows backward compatibility for existing scripts
    Use WorkOrderApi
    """
    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()

        self.logger = api_client.configuration.packagelogger
        self.logger.warning("WorkOrderIntegrationApiApi is obsolete, please"
                            " use WorkOrderAPI instead. You code will still"
                            " execute via WorkOrderIntegrationApiApi")
        self._workorderapi = WorkOrderApi(api_client)
        self.work_order_integration_api_add_work_task = \
            self._workorderapi.work_order_integration_api_add_work_task

        self.work_order_integration_api_add_work_task_with_http_info = \
            self._workorderapi.work_order_integration_api_add_work_task_with_http_info

        self.work_order_integration_api_get = \
            self._workorderapi.work_order_integration_api_get

        self.work_order_integration_api_get_with_http_info = \
            self._workorderapi.work_order_integration_api_get_with_http_info

        self.work_order_integration_api_get_0 = \
            self._workorderapi.work_order_integration_api_get_0

        self.work_order_integration_api_get_0_with_http_info = \
            self._workorderapi.work_order_integration_api_get_0_with_http_info

        self.work_order_integration_api_post = \
            self._workorderapi.work_order_integration_api_post

        self.work_order_integration_api_post_with_http_info = \
            self._workorderapi.work_order_integration_api_post_with_http_info

        self.work_order_integration_api_put = \
            self._workorderapi.work_order_integration_api_put

        self.work_order_integration_api_put_with_http_info = \
            self._workorderapi.work_order_integration_api_put_with_http_info