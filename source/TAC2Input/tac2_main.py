
# -*- coding: utf-8 -*-

__author__ = "Wilson D'Souze (WLDSZ)"
__copyright__ = "(c)2019 Vestas Technology R&D"
__version__ = "0.0.0"


import os
import shutil
import re


class main_class(object):

    def __init__(self,inputFile,derotatedCoordinates):

        print('Initialising TAC2 Input Class\n')
        self.min_radius = 0
        self.max_radius = 0        
        self.create_radius_folder(derotatedCoordinates)
        self.find_min_max_Radius(inputFile)
    
    def sorted_alphanumberic(self,l ):
       
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key = alphanum_key)

    def create_radius_folder(self,derotatedCoordinates):
        try:
            for cut_section in derotatedCoordinates:
                aerofoilDIR = os.path.dirname(''.join(cut_section))
                aerofoilname = os.path.basename(''.join(cut_section))
                section = aerofoilname.split('_')
                sec = section[3].split('.')

                # Creating Radius folder
                radius_location = aerofoilDIR + "\\Radius_" + str(int(sec[0]))
                if not os.path.exists(radius_location):
                    os.mkdir(radius_location)
                    shutil.move(cut_section,radius_location)

                    # Renaming each cut section as mentioned in aerotex software
                    src = os.path.join(radius_location,aerofoilname)
                    dst = radius_location + "\\TAC_CRD.dat"
                    os.rename(src,dst)            
        except:
            print("Error - Creating Radius folder")
    
    def find_min_max_Radius(self,input_file):
        try:
            fileID = open(input_file, 'r')
            filetext = fileID.read()
            fileID.close()

            fileLines = filetext.split('\n')

            for i in range(0, len(fileLines)):
                line = fileLines[i].split(',')

                if 'minimum' in line[0].casefold():
                    self.min_radius = line[1].lstrip()
                
                if 'maximum' in line[0].casefold():
                    self.max_radius = line[1].lstrip()
            
            self.match_sections(self.min_radius,self.max_radius)   
        except:
            print("Error - Finding min and max")
        
    def match_sections(self,min_radius,max_radius):
        try:
            print("Matching Begin")
            shutil.rmtree(".\\test\\V136_Aerotex_Values\\")            
            print("Existing Aerotex_Values are Removed")
            min_radius = "Radius_"+str(min_radius)
            max_radius = "Radius_"+str(max_radius)
            min_index = 0
            max_index = 0
            main_path = ".\\test\\V136_TAC2_Input_Files"
            windspeed_list = os.listdir(main_path)
            sorted_windspeed_list = self.sorted_alphanumberic(windspeed_list)
            cutsection_path = ".\\test\\V136_Bespoke"
            for i in range(len(sorted_windspeed_list)):
                windspeed_path = os.path.join(main_path,sorted_windspeed_list[i])
                radius_list = os.listdir(windspeed_path)
                sorted_radius_list = self.sorted_alphanumberic(radius_list)
                for j in range(len(sorted_radius_list)):
                    if(min_radius == sorted_radius_list[j]):
                        min_index = j
                    elif(max_radius == sorted_radius_list[j]):                        
                        max_index = j
                max_index = max_index +1
                required_list = sorted_radius_list[min_index:max_index]
                for k in range(len(required_list)):
                    each_Section = os.path.join(windspeed_path,required_list[k])
                    if not os.path.exists(".\\test\\V136_Aerotex_Values"):
                        os.mkdir(".\\test\\V136_Aerotex_Values")
                    destination = os.path.join(".\\test\\V136_Aerotex_Values\\Inputs\\",sorted_windspeed_list[i],required_list[k])

                    shutil.copytree(each_Section,destination)                    
                    try:
                        cut_section = os.path.join(cutsection_path,required_list[k])
                        TAC2_CRD = os.listdir(cut_section)
                        src = os.path.join(cut_section,TAC2_CRD[0])
                        shutil.copy(src,destination)
                        ihb_src = ".\\test\\V136_BEM_WORK_DIR\\IHB"
                        ihb_dst = destination.replace("Inputs","Outputs")
                        ihb_dst = os.path.join("",ihb_dst)
                        shutil.copytree(ihb_src,ihb_dst)
                    except:
                        print("Cut Section Not Found")
            print("Aerotex Output Generated")
            print("END")
        except:
            print("Error - Matching Section and cut section")