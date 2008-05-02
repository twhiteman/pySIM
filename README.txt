This is for running the pySimReader application. The SmartCard DLL library
that will be used by pySimReader should be compiled and placed into this
directory.

pySimReader will communicate with the DLL and the DLL communicates with the
Microsoft SmartCard Base Components and vice versa.

#####################
Build Requirements:

* Microsoft Visual Studio
* Swig
* Python
* wx-python

#####################
Build Instructions:

1. Build the PCSC dll and wrappers, follow the readme in PCSCHandle.
2. If using Python2.4 or above, rename "_PCSCHandle.dll" to "_PCSCHandle.pyd",
   otherwise you'll get python import errors when trying to run the program.

#####################
Running instructions:

# To start the application, run:
python pySimReader.py

