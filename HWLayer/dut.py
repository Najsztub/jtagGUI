# Device Under Test Class

class Logic:
  """ Base BSDL logic class with AST property """
  def __init__(self, ast=None):
    self._ast = ast

  @property
  def ast(self):
    return self._ast

  @ast.setter
  def ast(self, ast):
    self._ast = ast
    self.parseAst()
    
  def parseAst(self):
    pass

# Pin - physical connection
class Pin(Logic):
  def __init__(self):
    self.port = Port()
    self.name = None

  @property
  def read(self):
    return self.port.read

  @read.setter
  def read(self, value):
    self.port.read = value

  @property
  def write(self):
    return self.port.write

  @write.setter
  def write(self, value):
    self.port.write = value

# Port - Unit functional representation of pin or group of pins
class Port(Logic):
  def __init__(self):
    self.name = 'MISSING'
    self.pins = []
    self.type = "-"
    self.dim = None
    self.is_set = False
    # Add multiple cells and differentiate behaviour according to cell function
    self.in_cell = None
    self.out_cell = None

  def reset(self):
    if self.in_cell is not None:
      self.in_cell.reset()
    if self.out_cell is not None:
      self.out_cell.reset()
    self.is_set = False

  @property
  def read(self):
    if self.in_cell is None: return None
    return self.in_cell.bsr_in

  @read.setter
  def read(self, value):
    if self.in_cell is None: pass
    self.is_set = True
    self.in_cell.bsr_in = value

  @property
  def write(self):
    if self.out_cell is None: return None
    return self.out_cell.bsr_out

  @write.setter
  def write(self, value):
    if self.out_cell is None: pass
    self.is_set = True
    self.out_cell.bsr_out = value

  
# PortMapper - Represent pin-port map
class PortMapper(Logic):
  def __init__(self):
    self.pins = {}
    self.ports = {}
    self.ports_group = []

  def parsePortDef(self, ast):
    for group_id, gr in enumerate(ast):
      self.ports_group.append([])
      if 'bit_vector' in gr['port_dimension']:
        for pid in range(int(gr['port_dimension']["bit_vector"][0]), int(gr['port_dimension']["bit_vector"][2])+1):
            port_name_id = '{0}({1})'.format(gr["identifier_list"][0], pid)
            new_port = Port()
            new_port.name = port_name_id.upper()
            new_port.type = gr['pin_type']
            new_port.dim = gr['port_dimension']
            self.ports[new_port.name] = new_port
            self.ports_group[group_id].append(new_port)
      else:
        for port in gr["identifier_list"]: 
          new_port = Port()
          new_port.name = port.upper()
          new_port.type = gr['pin_type']
          new_port.dim = gr['port_dimension']
          self.ports[new_port.name] = new_port
          self.ports_group[group_id].append(new_port)

  def parsePinDef(self, ast):
    for p in ast:
      pin_list_len = len(p['pin_list'])
      for pid, pn in enumerate(p['pin_list']):
        port_name = p['port_name'].upper()
        # Create pin(n) in case of multiple pins in 'pin_list'
        if pin_list_len > 1:
          port_name = '{0}({1})'.format(port_name, pid)
        new_pin = Pin()
        new_pin.name = pn.upper()

        # Create port if one does not exist
        if port_name not in self.ports:
          new_port = Port()
          new_port.name = port_name
          self.ports[new_port.name] = new_port
        new_pin.port = self.ports[port_name]
        new_pin.port.pins.append(new_pin)
        self.pins[new_pin.name] = new_pin


# Cell - BSR cell. Can be associated with Port, but not 
class Cell(Logic):
  """
  BSR Cell definition
  """

  def __init__(self, dut):
    self.dut = dut
    
    self._bsr_out = None
    self._bsr_in = None

    self.port = None
    self.control = None
    self.function = None
    self.index = None

    self.reset_val = '1'

  def parseAst(self):
    cell = self._ast
    cell_spec = cell['cell_info']["cell_spec"]

    # Assign BSR index
    self.number = int(cell["cell_number"])

    # Assign function name
    self.function = cell_spec['function'].upper()

    # Collapse port name
    if type(cell_spec['port_id']) is list: 
      port_name = ''.join(cell_spec['port_id']).upper()
      cell_spec['port_id'] = port_name
    else:
      port_name = cell_spec['port_id'].upper()

    # Assign cells to ports
    # Assign port logic based on cell type
    if port_name in self.dut.ports:
      self.port = self.dut.ports[port_name]
      if self.function in ["INPUT", "CLOCK", "OBSERVE_ONLY"]:
        self.port.in_cell = self
      elif self.function in ["OUTPUT2", "OUTPUT3"]:
        self.port.out_cell = self
        if self.port.in_cell is None:
          self.port.in_cell = self
      elif self.function in ["BIDIR"]:
        self.port.in_cell = self
        self.port.out_cell = self

    # Reference controll cell
    if "input_or_disable_spec" in cell['cell_info']: 
      cell['ctrl'] = cell['cell_info']["input_or_disable_spec"]
      self.control = self.dut.bsr_cells[int(cell['ctrl']["control_cell"])]
      if cell['ctrl']["disable_value"] == '1':
        disable_value = '1'
      else:
        disable_value = '0'
      # Set disable value and 
      self.control.disable_value = disable_value
      self.control.reset_val = disable_value
      self.control.bsr_out = disable_value


    # Add safe bit as default out value
    if "safe_bit" in cell_spec and cell_spec["safe_bit"] == '0' :
      self.reset_val = '0'
    self._bsr_out = self.reset_val

  def reset(self):
    self._bsr_out = self.reset_val
    self.disable()

  @property
  def bsr_out(self):
    return self._bsr_out

  @bsr_out.setter
  def bsr_out(self, value):
    self.enable()
    self._bsr_out = value

  @property
  def bsr_in(self):
    return self._bsr_in

  @bsr_in.setter
  def bsr_in(self, value):
    self._bsr_in = value

  def enable(self):
    if self.control is None: return
    if self.control.disable_value == '0':
      self.control.bsr_out = '1'
    else:
      self.control.bsr_out = '0'
  
  def disable(self):
    if self.control is None: return
    self.control.bsr_out = self.control.disable_value

  
class DUT:
  def __init__(self, ast=None, idcode=None):
    # Create empty placeholders
    self.inner_id = None
    self.idcode = None
    self.name = ''
    self.package = ''

    self.chain_id = None

    self.ast = None

    # Initialize the mapper
    self.portMapper = PortMapper()
    self.pins = self.portMapper.pins
    self.ports = self.portMapper.ports

    self.registers = [["BYPASS", 1]]
    self.instructions = []

    self.active_instruction = None

    self.bsr_def = ()
    self.bsr_cells = None

    if ast is not None:
      self.addAST(ast)
    elif idcode is not None:
      self.idcode = idcode

  def addAST(self, ast):
    self.ast = ast
    
    # Assign name, package and ID
    self.name = ''.join(self.ast["component_name"])
    self.package = self.ast["generic_parameter"]["default_device_package_type"]
    if self.idcode is None: self.idcode = self.getBSDL_IDCODE()

    # Discover regs and instructions
    self.registers = [["BYPASS", 1]]
    self.instructions = []
    self.addRegisters()
    self.addInstructions()

    # Create port list first
    ports = []
    if self.ast["logical_port_description"] is not None:
      self.portMapper.parsePortDef(self.ast["logical_port_description"])

    # Create pin list and dict
    self.portMapper.parsePinDef(self.ast['device_package_pin_mappings'][0]['pin_map'])

  def setPort(self, port, key, value):
    pid = [i for i, x in self.pins.items() if x['port_name'] == port] 
    for p in pid:
      self.pins[p][key] = value

  def regLen(self, reg):
    r_len = [r[1] for r in self.registers if r[0] == reg]
    if len(r_len) == 0: return None
    return r_len[0]
  
  def getBSDL_IDCODE(self):
    if "idcode_register" not in self.ast["optional_register_description"]:
      idcode = [''.join(reg["idcode_register"]) for reg in self.ast["optional_register_description"] if "idcode_register" in reg]
    else:
      idcode = [''.join(self.ast["optional_register_description"]["idcode_register"])]
    return idcode[0]

  def cmpID(self, idcode):
    if self.idcode is None: return False
    # Include X in IDCODE
    code_mask = [i for i, c in enumerate(self.getBSDL_IDCODE()) if c.upper() == 'X']
    if len(code_mask) > 0:
      dev_id = list(idcode)
      for x in code_mask:
        dev_id[x] = 'X'
      dev_id = ''.join(dev_id)
      return dev_id == self.getBSDL_IDCODE()
    else: 
      return idcode == self.getBSDL_IDCODE()

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
    # TODO: Fix in cases if BSR = BOUNDARY
    if 'BSR' not in [r[0] for r in self.registers] and 'BOUNDARY' not in [r[0] for r in self.registers]: 
      self.registers.append(["BSR", int(self.ast["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_length"])])
    
    # "optional_register_description" - description of registers. Can be list of dicts or a dict
    # Pack in list if dict
    if hasattr(self.ast["optional_register_description"], 'keys'):
      reg_descast = [self.ast["optional_register_description"]]
    else:
      reg_descast = self.ast["optional_register_description"]
    instr = []
    for desc in reg_descast:
      reg_keys = [k for k in desc.keys()]
      reg_cont = ''.join(desc[reg_keys[0]])
      inst_len = len(reg_cont)
      inst_name = reg_keys[0].upper().replace('_REGISTER', '')
      # Add register
      instr.append([inst_name, inst_len])
    # "register_access_description" - register names + len + instr
    regsast = self.ast["register_access_description"]

    for reg in regsast:
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
        # TODO: FIx
        if reg_len is None:
          reg_len = int(self.ast["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_length"])
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

    self.bsr_cells = tuple(Cell(self) for _ in range(int(self.ast["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_length"])))
    for cell in ast_cells:
      cell_id = int(cell["cell_number"])
      self.bsr_cells[cell_id].ast = cell

    # Decide which cells to use as input cell
    # INPUT type has precedence over other types
    self.bsr_in_cells = []
    for c in self.bsr_cells:
      if c.function not in ['INPUT', 'CLOCK', 'BIDIR', 'OUTPUT2', 'OUTPUT3']: continue
      self.bsr_in_cells.append(c)

  def parseBSR(self, bsr):
    bsr_len = len(self.bsr_cells)
    for c in self.bsr_in_cells:
      # WARNING: Reverse addressing
      c.bsr_in = bsr[bsr_len - c.number - 1]

  def setBSR(self):
    bsr_len = len(self.bsr_cells)
    # Set BSR depending on cell state
    # bsr[bsr_len - 1 - c['cell_id']] = str(out_val)
    # TODO: Fix set
    nset = 1
    bsr = [ '1' if c.bsr_out == '1' else '0' for c in reversed(self.bsr_cells)]
    bsr = ''.join(bsr)
    return (nset, bsr)

  def readBSR(self, bsr):
    self.bsr.reg = bsr
    self.bsr.parseBSR()
