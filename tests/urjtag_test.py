import urjtag

urc1 = urjtag.chain()

urc1.cable('usbblaster')        
urc1.reset()                                      
urc1.addpart(10)                                                      
urc1.addpart(4)                                                       

urc1.part(1)                                                          
urc1.set_instruction('BYPASS')     

urc1.shift_ir()                                                       
urc1.shift_dr()                                                       


urc1.part(0)                                                          
urc1.add_register('BSR', 240)                                         
urc1.add_instruction('SAMPLE', '0000000101', 'BSR')                   
urc1.set_instruction('SAMPLE')                                        
                                                       

urc1.shift_ir()                                                       
urc1.shift_dr()                                                       

dr = urc1.get_dr_out_string()                                               
print(dr)