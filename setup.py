import cx_Freeze
import sys


base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

exe = [cx_Freeze.Executable("gui.py", base=base)]
files = ["C:/Users/Evnica/Anaconda3/DLLs/tcl86t.dll",
         "C:/Users/Evnica/Anaconda3/DLLs/tcl86t.dll",
         "icon.ico"]

cx_Freeze.setup(
    name="Interpolation",
    options={"build_exe": {"packages": ["tkinter", "numpy", "decimal", "dateutil", "enum",
                                        "statistics", "random", "tkinter.filedialog", "tkinter.messagebox",
                                        "ntpath", "time", "scipy", "datetime"],
                           "include_files": files
                          }
            },
    version="0.01",
    description="Spatio-temporal interpolation tool",
    executables=exe
    )
