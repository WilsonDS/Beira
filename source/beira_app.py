import os
import sys
from tkinter import Tk
from tkinter import filedialog
from beira.main import beira_class
from aerodata.aerodata import aerodata_class
from TAC2Input.tac2_main import main_class
from IHBInput.ihb_main import ihb_class

if __name__ == "__main__":

    if len(sys.argv) == 2:
        inputFile = sys.argv[1]
        if not os.path.exists(inputFile):
            sys.exit("\n/!\\ '%s' not available. Execution stopped." %
                     (inputFile))
    else:
        inputFile = 'beira.dat'

    if not os.path.exists(inputFile):
        root = Tk()
        root.overrideredirect(1)
        root.withdraw()
        inputFile = filedialog.askopenfilename(
            parent=root, title='Choose the Beira input file')

    # Initalize Beira Class
    try:
        program = beira_class(inputFile)
        program.run()
    except:
        print('Exit with Errors -- Beira Class')
        
    # Initaialize Aerodata Class
    try:
        coordinatesFiles = os.listdir('C:\\Repo\\tools_dev\\Beira\\test\\V136_Bespoke')
    
        for i in range(0,len(coordinatesFiles)):
            coordinatesFiles[i] = os.path.join('C:\\Repo\\tools_dev\\Beira\\test\\V136_Bespoke', coordinatesFiles[i] )
    
        aerodata = aerodata_class()
        derotatedCoordinates = aerodata.derotate(coordinatesFiles)
        print(derotatedCoordinates)
    except:
        print('Exit with Errors -- Aerodata Class')
       
    # Passing TAC2 Inputs to Aerotex Software and get TAC2 Outputs
    try:
        main_class(inputFile,derotatedCoordinates)
    except:
        print('Exit with Errors -- TAC2 Input Class')
       
    # Reading TAC2 outputs and modify the file and pass to IHB Software and get IHB outputs
    try:
        ihb_class(inputFile)
    except:
        print('Exit with Errors -- TAC2 Input Class')