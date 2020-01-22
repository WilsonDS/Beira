
# -*- coding: utf-8 -*-

__author__ = "Wilson D'Souze (WLDSZ)"
__copyright__ = "(c)2019 Vestas Technology R&D"
__version__ = "0.0.0"


import os
import shutil
import re


class ihb_class(object):

    def __init__(self,inputFile):
        print('Initialising IHB Input Class\n')
        self.inputFile = inputFile
        self.read_IHB_Input(".\\test\\V136_Aerotex_Values\\Outputs")
    def sorted_alphanumberic(self,l ):
       
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key = alphanum_key)
    
    def read_IHB_Input(self,path):
        try:
            print("Reading IHB Input")
            shutil.rmtree(".\\test\\V136_IHB_Values\\")  
            print(path)
            main_path = path
            windspeed_list = os.listdir(main_path)
            sorted_windspeed_list = self.sorted_alphanumberic(windspeed_list)
            for i in range(len(sorted_windspeed_list)):
                windspeed_path = os.path.join(main_path,sorted_windspeed_list[i])
                radius_list = os.listdir(windspeed_path)
                sorted_radius_list = self.sorted_alphanumberic(radius_list)
                for j in range(len(sorted_radius_list)):
                    each_Section_IHB_Input = os.path.join(windspeed_path,sorted_radius_list[j])
                    print(each_Section_IHB_Input)
                    IHB_Output = os.listdir(each_Section_IHB_Input)
                    ihb_dst = each_Section_IHB_Input.replace("\\V136_Aerotex_Values\\Outputs","\\V136_IHB_Values\\Inputs")
                    inp_file = os.path.join(ihb_dst,IHB_Output[0])
                    shutil.copytree(each_Section_IHB_Input,ihb_dst)
                    try:
                        fileID = open(inp_file, 'r+')
                        filetext = fileID.read()
                        
                        fileLines = filetext.split('\n')
                        print(fileLines[1])    
                        
                        line = fileLines[1].split("!")
                        print(line[0])
                        print(line[0].replace("2","1")) 

                        fileID.close()   
                                            
                    except:
                        print("Error - Finding min and max")
            #print("IHB Output Generated")
            print("END")
        except:
            print("Error - Reading IHB Input")