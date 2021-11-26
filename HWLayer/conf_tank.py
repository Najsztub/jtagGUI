# BDSL file definitions library in SQLite

import zlib
import sqlite3
import json
import os
from datetime import datetime

CABLES_DICT = [
  "ARCOM", "ByteBlaster", "DLC5", "EA253", "EI012", "FT2232", "ARM-USB-OCD", "ARM-USB-OCD-H", "Flyswatter", "gnICE", "gnICE+", "JTAGkey", 
  "JTAGv3", "JTAGv5", "KT-LINK", "milkymist", "OOCDLink-s", "Signalyzer", "Turtelizer2", "USB-JTAG-RS232", "usbScarab2", "USB-to-JTAG-IF", 
  "DigilentHS1", "FT4232", "gpio", "ICE-100B", "IGLOO", "jlink", "KeithKoep", "Lattice", "Minimal", "MPCBDM", "TRITON", "UsbBlaster", 
  "vsllink", "WIGGLER", "WIGGLER2", "xpc_ext", "xpc_int", "DirtyJTAG"
]

class BSDLtank:
  def __init__(self, db_file):
    self.db_file = db_file
    if os.path.isfile(db_file):
      self.conn = sqlite3.connect(db_file)
    else:
      self.conn = sqlite3.connect(db_file)
      self.createDB()

  def createDB(self):
    c = self.conn.cursor()

    # Create table
    c.execute("""
    CREATE TABLE bsdl (
      id INTEGER PRIMARY KEY, 
      date_add text not null, 
      idcode text not null, 
      source text,
      name text, 
      zip_ast blob
    )""")
    self.conn.commit()
    c.execute("""
    CREATE TABLE settings (
      setting text PRIMARY KEY, 
      value text
    )
    """)
    self.conn.commit()

  def getSetting(self, key=None):
    c = self.conn.cursor()
    if key is None:
      c.execute('SELECT * FROM settings')
      return c.fetchall()
    else:
      c.execute('SELECT value FROM settings where setting=?', (key,))
      return c.fetchone()

  def setSetting(self, key, value):
    c = self.conn.cursor()
    c.execute('REPLACE INTO settings (setting, value) VALUES(?, ?)', (key, value))
    self.conn.commit()

  def addBSDL(self, idcode, name=None, source=None, ast=None):
    if ast is not None:
      ast = zlib.compress(json.dumps(ast).encode('utf-8'))
    ts = str(datetime.now())
    c = self.conn.cursor()

    c.execute(
      'INSERT INTO bsdl (date_add, idcode, source, name, zip_ast) VALUES (?,?,?,?,?)', 
      (ts, idcode, source, name, ast)
    )
    self.conn.commit()
    c.execute("SELECT id, name, date_add, idcode, source, 1 as has_ast FROM bsdl WHERE date_add=?", (ts,))
    bsdl = c.fetchone()
    # Convert 5th item to Bool
    bsdl = list(bsdl)
    bsdl[5] = (bsdl[5] == 1)

    return bsdl

  def delBSDL(self, id):
    c = self.conn.cursor()
    c.execute('DELETE FROM bsdl WHERE id=?', (id,))
    self.conn.commit()

  def readBSDL(self, id):
    c = self.conn.cursor()
    c.execute('SELECT * FROM bsdl WHERE id=?', (id,))
    bsdl = c.fetchone()
    ast = None
    if bsdl[5] is not None:
      ast = json.loads(zlib.decompress(bsdl[5]).decode('utf-8'))
    return {
      'id': bsdl[0],
      'date_add': bsdl[1],
      'idcode': bsdl[2],
      'source': bsdl[3],
      'name': bsdl[4],
      'ast' : ast
    }
  
  def getTab(self):
    c = self.conn.cursor()
    c.execute('SELECT id, name, date_add, idcode,  source, CASE WHEN zip_ast is not NULL THEN 1 ELSE 0 END as has_ast FROM bsdl')
    bsdl = c.fetchall()
    # Convert 5th item to Bool
    for row_id in range(len(bsdl)):
      bsdl[row_id] = list(bsdl[row_id])
      bsdl[row_id][5] = (bsdl[row_id][5] == 1)
      # Fix datetime
      bsdl[row_id][2] = bsdl[row_id][2].split('.', 1)[0]
    return bsdl

  def getCodes(self, idcode):
    c = self.conn.cursor()
    c.execute("SELECT id, zip_ast FROM bsdl WHERE ? LIKE REPLACE(idcode, 'X', '_') ORDER BY date_add DESC", (idcode, ))
    bsdl = c.fetchone()
    # Convert 2nd item to Bool
    if bsdl is None:
      return None
    if bsdl[1] is not None:
      bsdl = list(bsdl)
      bsdl[1] = json.loads(zlib.decompress(bsdl[1]).decode('utf-8'))
    return bsdl

  def __del__(self):
    self.conn.close()