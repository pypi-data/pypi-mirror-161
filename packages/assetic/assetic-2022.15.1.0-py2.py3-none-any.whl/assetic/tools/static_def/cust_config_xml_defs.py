# a dict of core asset fields where the key is defined in customer
# xml and the value is the oData value
asset_core_fields_dict = {
    'asset_id': 'ComplexAssetId',
    'asset_name': 'ComplexAssetName',
    'asset_external_identifier': 'ComplexAssetExternalIdentifier',
    'asset_category': 'ComplexAssetAssetCategory',

    'asset_criticality': 'ComplexAssetCriticality',

    'asset_class': 'ComplexAssetClass',
    'asset_sub_class': 'ComplexAssetSubClass',

    'asset_type': 'ComplexAssetType',
    'asset_sub_type': 'ComplexAssetSubType',

    'asset_maintenance_type': 'ComplexAssetMaintenanceSubType',
    'asset_maintenance_subtype': 'ComplexAssetMaintenanceType',

    'assetic_criticality': "ComplexAssetCriticality",
    'asset_work_group': "ComplexAssetWorkGroup",
    'status': "CAStatus",
}

# todo the labels in the odata assets info don't exactly match cloud upload column names
address_fields_dict = {
    'street_number': 'ComplexAssetStreetNumber',
    'street_address': 'ComplexAssetStreetAddress',
    'city_suburb': 'ComplexAssetCitySuburb',
    'state': 'ComplexAssetState',
    'zip_postcode': 'ComplexAssetZipPostcode',
    'country': 'Country',  # todo this doesn't exist in oData

}

# todo create a mandatory field dict for components, nms, addresses, etc.

component_fields_dict = {
    'design_life': "ComponentDesignLife",
    # "material_type": "ComponentPrimaryMaterial",
    "material_type": "Primary Material",  # todo this has an incorrect reference in oData
    'label': 'ComponentName',
    'name': 'ComponentId',
    'component_type': 'ComponentType',
    # 'dimension_unit': 'ComponentDimensionUnit',# todo this has an incorrect reference in oData
    'dimension_unit': 'Unit',  # todo this has an incorrect reference in oData
    'network_measure_type': 'Network Measure Type'  # todo this doesn't exist in oData
}

nm_fields_dict = {
    'network_measure': 'Measurement',
    'component_type': 'ComponentType',
    'unit': 'MeasurementUnit',
    'record_type': 'RecordType',
    'network_measure_type': 'MeasurementType',
    'length': 'Length',
    'width': 'Width',
    'height': 'HeightUnit',
    'shape_name': 'Shape',
    'length_unit': 'LengthUnit',
    'width_unit': 'WidthUnit',
    'height_unit': 'HeightUnit',
    'label': 'ComponentName'
}

# i think the dx names for these are all wacky
funcloc_fields_dict = {
    'asset_id': 'Asset', # FL dx upload != oData
    'functional_location_id':  'Functional Location Id',
    'functional_location_name': 'Functional Location Name',
    'functional_location_type': 'Functional Location Type',
}
