# Device Under Test Class

# Pin - physical connection
# Port - Unit functional representationof pin or group of pins
# Cell - BSR cell. Can be associated with Port, but not necessarily

class DUT:
  def __init__(self, ast):
    self.ast = ast
    
    # Assign name and package
    self.name = ''.join(self.ast["component_name"])
    self.package = self.ast["generic_parameter"]["default_device_package_type"]
    
    # Create pin dict
    pins = self.ast['device_package_pin_mappings'][0]['pin_map']
    plist = [{'pin_id': pn, 'name': p['port_name']} for p in pins for pn in p['pin_list']]

    # For searching pins by port
    self.port_dict = [p['name'] for p in plist]
    

    # Save as dict of dicts
    self.pins = dict([(p[0], p[1]) for p in enumerate(plist)])

    # Add port logic
    if self.ast["logical_port_description"] is not None:
      for group_id, gr in enumerate(self.ast["logical_port_description"]):
        for port in gr["identifier_list"]:
          self.setPort(port, "port_group", group_id)
          self.setPort(port, "pin_type", gr['pin_type'])
    
    # Make pins addressable by pin_id
    self.pin_dict = dict([(p[1]['pin_id'], p[0]) for p in enumerate(plist)])

  def setPort(self, port, key, value):
    pid = [i for i, x in self.pins.items() if x['name'] == port] 
    for p in pid:
      self.pins[p][key] = value
  
  def prepareBSR(self):
    pass