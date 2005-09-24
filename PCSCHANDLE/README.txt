This is for building the Smart Card DLL library that will be used by
pySimReader.

pySimReader will communicate with the DLL and the DLL communicates with the
Microsoft SmartCard Base Components and vice versa.

SWIG was used to generate the python wrapper files for accessing the
DLL library.

Building instructions:

# Build the wrapper code for python to DLL using SWIG
REBUILD.BAT

# Open Microsoft or whatever compiler you use and compile the c++ files.
PCSCHANDLE.CPP
PCSCHANDLE_WRAP.CPP

# Copy the generated _PCSCHandle.dll and PCSCHANDLE.PY files into the
# pySimReader directory.
