## JTAGViewer

This code presents an approach to combine 3 tools into a JTAG test chain visualizer.

* [UrJTAG](http://urjtag.org/) Python bindings for hardware backend;
* [TatSu](https://tatsu.readthedocs.io/en/stable/) grammar parser for parsing external BSDL files. This software uses BSDL grammar definition from [cyrozap/python-bsdl-parser](https://github.com/cyrozap/python-bsdl-parser);
* [wxPython](https://www.wxpython.org/) for GUI interface.



### Installation and running

This software was developed under Python 3.9. And uses the mentioned above packages (wxPython, TatSu and UrJTAG Python bindings). For now it works just by running `main.py`.

I used it together with a STM32 USBBlaster clone (e.g. [DirtyJTAG](https://github.com/jeanthom/DirtyJTAG)) for interfacing with JTAG, but any of the probes supported by UrJTAG should work.