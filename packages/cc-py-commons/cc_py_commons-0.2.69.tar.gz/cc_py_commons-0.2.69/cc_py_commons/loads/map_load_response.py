from datetime import date
from cc_py_commons.loads.load_schema import LoadSchema

def execute(freight_hub_json):
  freight_hub_json_copy = freight_hub_json.copy()
  pickup_date = freight_hub_json.get('pickupDate')

  if pickup_date:
    freight_hub_json_copy['pickupDate'] = date.fromtimestamp(int(pickup_date)/1000).isoformat()

  delivery_date = freight_hub_json.get('deliveryDate')

  if delivery_date:
    freight_hub_json_copy['deliveryDate'] = date.fromtimestamp(int(delivery_date)/1000).isoformat()

  return LoadSchema().load(freight_hub_json_copy)
