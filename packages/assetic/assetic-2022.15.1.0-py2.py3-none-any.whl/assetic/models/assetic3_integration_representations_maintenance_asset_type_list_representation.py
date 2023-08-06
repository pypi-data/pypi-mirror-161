from assetic.models.maintenance_asset_type_list_representation import MaintenanceAssetTypeListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceAssetTypeListRepresentation(MaintenanceAssetTypeListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceAssetTypeListRepresentation" class is deprecated, use "MaintenanceAssetTypeListRepresentation" instead',stacklevel=2)
		super(MaintenanceAssetTypeListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
