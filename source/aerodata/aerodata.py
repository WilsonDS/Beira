__author__ = "DISCE"
__version__= "0.0.0"
__date__="January 2020"
__copyright__= "Copyright 2019, Vestas Technology UK Ltd"
__email__="disce@vestas.com"

import sys
import os
import glob
import numpy as np
import subprocess as sp
from tkinter import Tk
from tkinter import filedialog
import multiprocessing
from multiprocessing import freeze_support
freeze_support()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class aerodata_class(object):

    def __init__(self):
        self.reset()
        self.load_settings()

    def reset(self):
        #reset all class data to initial status

        if __name__ == "__main__":
            self._location = os.getcwd()
        else:
            self._location = os.path.dirname(__file__)
        self._cwd = os.getcwd()
        self._xfoil_loc = ''
        self._xfoilDir = ''
        self._rfoil_loc = ''
        self._rfoilDir = ''
#        self._coordinatesDir = None
#        self._coordinatesFile = None
        self._parallel = False
        self._aerofoilPaths = []
        self._derotatedCoordinates =[]
        #default solver rfoil
        self._solver = 'rfoil'
        self._solverpath = ''
        self._solverDir =  ''
        self._process = None
        self._DERO = False   

        #global user_cores , number of available cores
        self._user_cores = multiprocessing.cpu_count()         

    def getDerotatedLocations(self):
        return self._derotatedCoordinates

    def getSolver(self):
        return self._solver
    
    def getSolverPath(self):
        return self._solverpath

    def set_solver(self, solver, solverloc = ''):
        if solver == 'xfoil':
            self._solver = 'xfoil'
            flag = self.set_xfoil_loc(solverloc)
            if flag == False:
                raise Exception('ERROR: Solver *.exe not found')

            self._solverpath = self._xfoil_loc
            self._solverDir =  self._xfoilDir    
        
        else:
            self._solver = 'rfoil'
            flag = self.set_xfoil_loc(solverloc)
            if flag == False:
                raise Exception('ERROR: Solver *.exe not found')
    
            self._solverpath = self._rfoil_loc
            self._solverDir =  self._rfoilDir
    
    #def loadAerofoilCoordinates
        #function to load aerofoil coordinates from a file

    #def setAerofoilCoordinates



    def derotate(self, coordinatesFiles =None):
        self.runPannelCode(coordinatesFiles , solver = 'xfoil',solverloc = '', DERO = True, saveDERO = True )
        return self._derotatedCoordinates

    def runPannelCode(self, coordinatesFiles =None , solver = 'rfoil',solverloc = '', DERO = False, saveDERO = False ):
        #prepare the specified solver to run in parallel with the user defined operations

        #store solver options
        if not DERO:
            saveDERO = False

        if solver == 'rfoil' and DERO:
            coordinatesFiles = self.derotate(coordinatesFiles)
            self._DERO = False
            self._saveDERO = False
        else:
            self._DERO = DERO
            self._saveDERO = saveDERO

        self.set_solver(solver, solverloc)
        
        if not coordinatesFiles is None:
            #load coordinates files and remove headers if needed
            self._coordinatesFile = coordinatesFiles
            self.load_aerofoils(coordinatesFiles)

        if self._aerofoilPaths is None:
            #If user did not set a coordinates file raise exception (options either load directly or an input)
            raise Exception('Coordinate files not set')

        #defined subprocess
        if self._parallel:
            # Multiprocessing

            processinputs = []
            for i in range(0,len(self._aerofoilPaths)):
                processinputs.append([self._aerofoilPaths[i]])
            with multiprocessing.Pool(processes=self._user_cores) as pool:
                try:
                    #pool = Pool(ncores)
                    #pool.starmap(yourfunction, arguments)
                    self._derotatedCoordinates = pool.starmap(self.subprocess, processinputs)
                    
                    print("   - Aerodynamic 2D computations achieved in parallel on %i CPU" % self._user_cores )
                finally:
                    pool.close()
                    pool.join()
        else:
            self._derotatedCoordinates = self.subprocess(self._aerofoilPaths)

    def subprocess(self, single_aerofoilPath):

        #nested function to issue comands to the console
        def issueCmd(cmd, echo = False):
            process.stdin.write(cmd + '\n')
            if echo:
                print(cmd)
            
        startupinfo = sp.STARTUPINFO()
        startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW

        #work in the folder where the coordinates file is located
        aerofoilDIR = os.path.dirname(''.join(single_aerofoilPath))
        aerofoilname = os.path.basename(''.join(single_aerofoilPath))
        os.chdir(aerofoilDIR)
        
        process = None
        #try the subprocess to make sure the current working folder can be restored
        try:

            # Calling solver with Popen
            # Carefull using the Popen and PIPE to communicate with the process
            # it needs to be closed and the outputs retreived to run correctly in parallel
            process = sp.Popen([self._solverpath], 
                stdin=sp.PIPE,
                stdout=sp.PIPE,
                stderr=None,
                startupinfo=startupinfo,
                encoding='utf8')

            # Loading geometry
            issueCmd('load %s' % "".join(aerofoilname))

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #                 Applying geometric parameter
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if self._DERO:
                # Rotating buffer airfoil
                issueCmd('')
                issueCmd('gdes')
                issueCmd('dero')
                issueCmd('unit')
                issueCmd('exec')
                issueCmd('')
            if self._saveDERO:
                #save and store location into the class of the derotated aerofoils
                issueCmd('save derotated_'+''.join(aerofoilname), True)
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #                finish
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            issueCmd('')
            issueCmd('')
            issueCmd('quit')
            output, errors = process.communicate()
            #print(output)
            process.stdin.close()
            # From popen

        except:
            if not process is None:
                process.terminate()
            raise Exception('Error: subprocess did not run correctly')

        os.remove(''.join(single_aerofoilPath)) 
        
        #return to orginal working dir
        os.chdir(self._cwd)

        return (os.path.join(aerofoilDIR,'derotated_'+''.join(aerofoilname)))

        
    def load_settings(self):
        #load xfoil location from loc file
        found = False

        if os.path.exists('xfoil.loc'):
            fid = open('xfoil.loc','r')
            xfoil_loc = fid.readline()
            fid.close()
            if os.path.exists(xfoil_loc):
                self._xfoil_loc = xfoil_loc
                found = True
                print('xfoil.exe loaded\n')
       
        if os.path.exists(os.path.join(self._location,'xfoil.exe')) and not found:
            self.set_xfoil_loc()
            print('xfoil.exe loaded\n')

        elif not found:
            self._xfoil_loc = ''
            print('Warning, xfoil.exe not found\n')

        found = False
        #load rfoil location from loc file
        if os.path.exists('rfoil.loc'):
            fid = open('rfoil.loc','r')
            rfoil_loc = fid.readline()
            fid.close()
            if os.path.exists(rfoil_loc):
                self._xfoil_loc=rfoil_loc
                print('rfoil.exe loaded\n')
                found = True

        if os.path.exists(os.path.join(self._location,'rfoil.exe')) and not found:
            self.set_rfoil_loc()
            print('rfoil.exe loaded\n')

        elif not found:
            self._rfoil_loc = ''
            print('Warning, rfoil.exe not found\n')

            
    def set_xfoil_loc(self, xfoil_loc = ''):

        if xfoil_loc == '':
            xfoil_loc = os.path.join(self._location,'xfoil.exe')

        if not os.path.exists(xfoil_loc):
            root = Tk()
            root.overrideredirect(1)
            root.withdraw()
            xfoil_loc = filedialog.askopenfilename(
                parent=root, title='Choose the xfoil.exe File')

        if os.path.exists(xfoil_loc):

            fid = open('xfoil.loc','w+')
            fid.write(xfoil_loc)
            fid.close()

            self._xfoil_loc = xfoil_loc
            self._xfoilDir = os.path.dirname(xfoil_loc)
            
            print('xfoil.exe loaded and stored sucessfully\n')
            return True
        else:
            print('Warning, xfoil.exe not found')
            return False

    def set_rfoil_loc(self, rfoil_loc = ''):
        if xfoil_loc == '':
            xfoil_loc = os.path.join(self._location,'rfoil.exe')

        if not os.path.exists(rfoil_loc):
            root = Tk()
            root.overrideredirect(1)
            root.withdraw()
            rfoil_loc = filedialog.askopenfilename(
                parent=root, title='Choose the rfoil.exe File')

        if os.path.exists(rfoil_loc):

            fid = open('rfoil.loc','w+')
            fid.write(rfoil_loc)
            fid.close()

            self._rfoil_loc = rfoil_loc
            self._rfoilDir = os.path.dirname(rfoil_loc)
            
            print('rfoil.exe loaded and stored sucessfully\n')
            return True
        else:
            print('Warning, rfoil.exe not found')
            return False

    def load_aerofoils(self, coordinatesFiles):
        self._parallel = False
        if isinstance(coordinatesFiles, list):
            if len(coordinatesFiles)>1:
                self._parallel = True
            for i in range(0, len(coordinatesFiles)):
                self._aerofoilPaths.append(self.clean_aerofoils(coordinatesFiles[i]))   
        else:
            self._aerofoilPaths = self.clean_aerofoils(coordinatesFiles)


    def clean_aerofoils(self, single_coordinatesFile):

        clean_file = False

        coordinatesFileDir = os.path.dirname(single_coordinatesFile)
        coordinatesFileName = os.path.basename(single_coordinatesFile)

        #read lines from coordinates file
        fid = open(single_coordinatesFile,'r')
        lines = fid.readlines()
        fid.close()

        #Check if files need to be cleaned from headers and errors in the coordinates
        n=0
        firstline = True
        while n < len(lines):
            singleline = lines[n].split()
            if len(singleline) > 0:
                if not is_number(singleline[0]):
                    clean_file = True
                    break
                elif len(singleline) > 2:
                    clean_file = True
                    break
            elif firstline:
                firstline = False
            else:
                clean_file = True
                break
            n=n+1
            
        if clean_file:
            #clean header


            m=0
            while m < len(lines):
                singleline = lines[m].split()
                if len(singleline) > 0:
                    if not is_number(singleline[0]):
                        lines.pop(m)
                    elif len(singleline)>2:
                        while len(singleline)>2:
                            singleline.pop() 
                        lines[m] = singleline[0]+' '+singleline[1]+'\n'
                    else:
                        m=m+1
                else:
                    lines.pop(m)

            aerofoilName = ''.join('clean_'+coordinatesFileName)
            aerofoilPath = os.path.join(coordinatesFileDir,aerofoilName)
            aerorfoilInput = open(aerofoilPath,'w+')
            aerorfoilInput.write(''.join(lines))
            aerorfoilInput.close()
        
        else:
            aerofoilPath = single_coordinatesFile
        return aerofoilPath

            
#if __name__ == "__main__":
##    use main for test only! Do not try to load it from another module
#
#    #coordinatesFiles = ['C:\\Repo\\tools_dev\\Beira\\test\\V136_Bespoke\\section_57000.dat']
#    
#    coordinatesFiles = os.listdir('C:\\Repo\\tools_dev\\Beira\\test\\V136_Bespoke')
#
#    for i in range(0,len(coordinatesFiles)):
#        coordinatesFiles[i] = os.path.join('C:\\Repo\\tools_dev\\Beira\\test\\V136_Bespoke', coordinatesFiles[i] )
#
#    aerodata = aerodata_class()
#    derotatedCoordinates = aerodata.derotate(coordinatesFiles)
#    print(derotatedCoordinates)


