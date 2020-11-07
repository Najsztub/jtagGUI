# Device Under Test Class

# Pin - physical connection
# Port - Unit functional representationof pin or group of pins
# Cell - BSR cell. Can be associated with Port, but not necessarily
  

class DUT:
  def __init__(self, ast=None, idcode=None):
    # Create empty placeholders
    self.inner_id = None
    self.idcode = None
    self.name = ''
    self.package = ''

    self.chain_id = None

    self.ast = None
    self.pins = None
    self.registers = [["BYPASS", 1]]
    self.instructions = []

    self.active_instruction = None

    self.bsr_def = ()

    if ast is not None:
      self.addAST(ast)
    elif idcode is not None:
      self.idcode = idcode

  def addAST(self, ast):
    self.ast = ast
    
    # Assign name, package and ID
    self.name = ''.join(self.ast["component_name"])
    self.package = self.ast["generic_parameter"]["default_device_package_type"]
    self.idcode = self.getID()

    # Discover regs and instructions
    self.addRegisters()
    self.addInstructions()

    # Create pin list and dict
    pins = self.ast['device_package_pin_mappings'][0]['pin_map']
    # Create pin(n) in case of multiple pins in 'pin_list'
    plist = []
    for p in pins:
      if len(p['pin_list']) > 1:
        # Loop over pins in 'pin_list'
        for i, pn in enumerate(p['pin_list']):
          plist.append({'pin_id': pn, 'port_name': '{0}({1})'.format(p['port_name'], i+1)})
      else:
        plist.append({'pin_id': p['pin_list'][0], 'port_name': p['port_name']})

    # For searching pins by port
    self.port_map = {}
    for id, pin in enumerate(plist):
      if pin['port_name'] in self.port_map:
        # Append id to port
        self.port_map[pin['port_name']].append(id)
        pass
      # Else create key and list
      self.port_map[pin['port_name']] = [id]

    # Save as dict of dicts
    self.pins = dict([(p[0], p[1]) for p in enumerate(plist)])

    # Add port logic
    if self.ast["logical_port_description"] is not None:
      for group_id, gr in enumerate(self.ast["logical_port_description"]):
        for port in gr["identifier_list"]:
          self.setPort(port, "port_group", group_id)
          self.setPort(port, "pin_type", gr['pin_type'])
          self.setPort(port, "read", '')
    
    # Make pins addressable by pin_id
    self.pin_dict = dict([(p[1]['pin_id'], p[0]) for p in enumerate(plist)])

  def setPort(self, port, key, value):
    pid = [i for i, x in self.pins.items() if x['port_name'] == port] 
    for p in pid:
      self.pins[p][key] = value
  
  def getID(self):
    if "idcode_register" not in self.ast["optional_register_description"]:
      idcode = [''.join(reg["idcode_register"]) for reg in self.ast["optional_register_description"] if "idcode_register" in reg]
    else:
      idcode = [''.join(self.ast["optional_register_description"]["idcode_register"])]
    return idcode[0]

  def addRegisters(self, name=None, length=None):
    # Manually add registers or discover from AST
    if name is not None and length is not None:
      self.registers.append([name, length])
      return
    if self.ast is None: return
    # Read registers from AST

    # Add IR first
    if 'IR' not in [r[0] for r in self.registers]: 
      self.registers.append(["IR", int(self.ast["instruction_register_description"]["instruction_length"])])
    
    # And now BSR
    if 'BSR' not in [r[0] for r in self.registers]: 
      self.registers.append(["BSR", int(self.ast["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_length"])])
    
    # "optional_register_description" - description of registers. Can be list of dicts or a dict
    # Pack in list if dict
    if hasattr(self.ast["optional_register_description"], 'keys'):
      reg_desc_ast = [self.ast["optional_register_description"]]
    else:
      reg_desc_ast = self.ast["optional_register_description"]
    instr = []
    for desc in reg_desc_ast:
      reg_keys = [k for k in desc.keys()]
      reg_cont = ''.join(desc[reg_keys[0]])
      inst_len = len(reg_cont)
      inst_name = reg_keys[0].upper().replace('_REGISTER', '')
      # Add register
      instr.append([inst_name, inst_len])
    # "register_access_description" - register names + len + instr
    regs_ast = self.ast["register_access_description"]
    add_regs = []
    for reg in regs_ast:
      reg_name = reg["register"]["reg_name"]
      reg_len = None
      if "reg_length" in reg['register']: reg_len = int(reg["register"]["reg_length"])
      for inst in reg["instruction_capture_list"]:
        # Append reg_len if None and instruction is in instr
        inst_name = inst["instruction_name"]
        if reg_len is None:
          reg_lens = [i for i,x in enumerate(instr) if x[0]==inst_name]
          if len(reg_lens) > 0: 
            # If reg is in instr, then take tength from there
            reg_len = instr[reg_lens[0]][1]
            # Also del the item from instr. I will use remaining not found instr as reg names
            del instr[reg_lens[0]]
        # Append register to self
        if reg_name not in [r[0] for r in self.registers]: self.registers.append([reg_name, reg_len])
        # Append instruction
        if inst_name not in [r[0] for r in self.instructions]: self.instructions.append([inst_name, None, reg_name])
    # Append remaining instr as registers
    for i in instr:
      # Append register to self
      if i[0] not in [r[0] for r in self.registers]: self.registers.append(i)
      # Append instruction
      if i[0] not in [r[0] for r in self.instructions]: self.instructions.append([i[0], None, i[0]])      

  def addInstructions(self, name=None, opcode=None, reg=None):
    # Manually add instructions or discover from AST
    if name is not None:
      self.instructions.append([name, opcode, reg])
      return
    if self.ast is None: return
    for inst in self.ast["instruction_register_description"]["instruction_opcodes"]:
      reg = None
      # If name is BYPASS, then assign BYPASS register
      if inst["instruction_name"] is None: reg = 'BYPASS'
      # Otherwise use BSR
      if reg is None: reg = "BSR"
      # Append if does not exist
      if inst["instruction_name"] not in [i[0] for i in self.instructions]:
        self.instructions.append([inst["instruction_name"], inst["opcode_list"][0], reg])
      # Update opcode if instruction present and no opcode
      else:
        iid = [i for i,x in enumerate(self.instructions) if x[0] == inst["instruction_name"]][0] 
        if self.instructions[iid][1] is None: self.instructions[iid][1] = inst["opcode_list"][0]

  def addCells(self):
    # TODO: Add cells manually
    if self.ast is None: return
    # Parse AST
    ast_cells = self.ast["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_register"]
    self.bsr_cells = [None,] * int(self.ast["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_length"])
    for cell in ast_cells:
      cell_id = int(cell["cell_number"])
      cell_spec = cell['cell_info']["cell_spec"]
      cell_spec['cell_id'] = cell_id
      if "input_or_disable_spec" in cell['cell_info']: cell_spec['ctrl'] = cell['cell_info']["input_or_disable_spec"]
      self.bsr_cells[cell_id] = cell_spec

    self.bsr_in_cells = [c for c in self.bsr_cells if c['function'].upper() in ['INPUT', 'CLOCK', 'BIDIR']]

  def parseBSR(self, bsr):
    for c in self.bsr_in_cells:
      port = c['port_id']
      id = c['cell_id']
      pin_id = self.port_map[port][0]
      self.pins[pin_id]['read'] = bsr[id]


  def readBSR(self, bsr):
    self.bsr.reg = bsr
    self.bsr.parseBSR()
