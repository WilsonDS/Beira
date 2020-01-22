# -*- coding: utf-8 -*-
from pyro.parsers import AeroInputFile, AeroOutputFile
import pyro
import numpy as numpy
import pandas as pandas
import math
from os import path
import os


class blade_class(object):

    def __init__(self, solver, bladeInp, bladeOut, vasLayout, bladeSectionFolder, weathertable, input_file, timeScheme=None):

        print('Loading blade geometry\n')
        # initialise blade]
        self.reset()
        self.input_path = input_file

        # load pyro data
        if solver == 'pyro':
            # check if input is available
            if bladeInp == '':
                raise Exception('pyro input file not found')

            abs_path = path.dirname(path.abspath(__file__))
            abs_path_rstrip = path.dirname(abs_path.rstrip('/'))

            bladeInp = path.join(abs_path_rstrip, bladeInp)
            bladeOut = path.join(abs_path_rstrip, bladeOut)

            self.loadPyroInput(bladeInp, logfile=None)
            self.loadPyroOutput(bladeOut, logfile=None)

        # load vtds data
        if solver == 'vts':
            raise Exception('VTS inputs not yet supported')

        # initialise vas layout
        self.loadVasLayout(vasLayout)

        self.weathertable = weathertable
        self.windspeed(self.weathertable)

        # load aerofoils
        self.loadAerofoils(bladeSectionFolder)

        print('Blade geometry Loaded\n')

    def reset(self):
        # reset blade class

        self.pyroIn = None
        # pyro_in contains
        self.radius = None
        self.chord = None
        self.twist = None
        self.rel_thickness = None

        self.pyroOut = None
        # pyro_out contains
        self.hub_height = None
        self.wind = None  # (atmospheric wind)
        self.v = None  # (array of local relative velocity)
        self.alpha = None  # (array of local angle of attack)

        # reset
        self.vasElements = None

        # reset aerofoil class
        self.aerofoil = []

    def loadPyroInput(self, pyroInputFile, logfile=None):
        # load blade geometry
        # consider using just the pyroIn
        self.pyroIn = AeroInputFile(pyroInputFile, logfile=None)
        self.radius = self.pyroIn.radius
        self.chord = self.pyroIn.chord
        self.twist = self.pyroIn.twist
        self.rel_thickness = self.pyroIn.thick

    def loadPyroOutput(self, pyroOutputFile, logfile=None):
        # check if there is an output, otherwise run pyro
        if pyroOutputFile == "":
            pyrosolve = pyro.main.PyroMain(self.pyroIn)
            pyrosolve()
            pyroOutputFile = self.pyroIn.split('inp')[0]+'out'

        # consider using just the pyroOut
        self.pyroOut = AeroOutputFile(pyroOutputFile, logfile=None)
        self.hub_height = self.pyroOut.hub_height
        self.wind = self.pyroOut.wind  # (atmospheric wind)
        self.v = self.pyroOut.v  # (array of local relative velocity)
        self.alpha = self.pyroOut.alpha  # (array of local angle of attack)
        self.radius_out = self.pyroOut.radius
        # load blade operation conditions

    def loadVasLayout(self, vasElements):
        self.vasElements = vasElements

    def loadAerofoils(self, bladeSectionFolder):
        self.bladeSectionFolder = bladeSectionFolder

        # cycle through aerofoils and radius and assign them to aerofoil class
        #self.aerofoil[0] = aerofoil_class()
    def finding_index_val(self, main_array, sub_array):
        numpy_array = numpy.array(main_array)
        index_val = numpy_array.tolist().index(sub_array)
        return index_val

    def windspeed(self, wsp):
        for wsp_val in wsp['wsp']:
            if not math.isnan(float(wsp_val)):
                try:
                    # index
                    index_val = self.finding_index_val(self.wind, wsp_val)
                    # Temperature
                    temp_val = self.finding_index_val(wsp['wsp'], wsp_val)
                    temp_val = wsp['temp'][temp_val]
                    # LWC
                    LWC_val = self.finding_index_val(wsp['wsp'], wsp_val)
                    LWC_val = wsp['lwc'][LWC_val]
                    # Time
                    Time_val = self.finding_index_val(wsp['wsp'], wsp_val)
                    Time_val = wsp['lwc'][Time_val]
                    self.get_AoA_V(wsp_val, index_val,
                                   temp_val, LWC_val, Time_val)
                except:
                    # Temperature
                    temp_val = self.finding_index_val(wsp['wsp'], wsp_val)
                    temp_val = wsp['temp'][temp_val]
                    # LWC
                    LWC_val = self.finding_index_val(wsp['wsp'], wsp_val)
                    LWC_val = wsp['lwc'][LWC_val]
                    # Time
                    Time_val = self.finding_index_val(wsp['wsp'], wsp_val)
                    Time_val = wsp['lwc'][Time_val]
                    self.linear_interpolation(
                        self.wind, wsp, wsp_val, temp_val, LWC_val, Time_val)
            else:
                print("NAN", index_val)

    def closest(self, lst, K):
        t = []
        for i in range(len(lst)):
            t.append(abs(lst[i]-K))

        min_index = t.index(min(t))
        val = {}
        val['min'] = lst[min_index - 1]
        val['max'] = lst[min_index]
        return val

    def linear_interpolation(self, windspeed, valid_json, wsp_val, temp_val, LWC_val, Time_val):
        try:
            # sort the wind speed
            windspeed.sort()

            # get closedt min and max val for interpolation
            self.interpolation_input_windspeed = self.closest(
                windspeed, wsp_val)

            # left and right wind speed
            min_index_val = self.finding_index_val(
                self.wind, self.interpolation_input_windspeed['min'])
            max_index_val = self.finding_index_val(
                self.wind, self.interpolation_input_windspeed['max'])

            # Angle of attack
            angle_of_attack_min = self.alpha[min_index_val]
            angle_of_attack_max = self.alpha[max_index_val]

            # Velocity
            velocity_min = self.v[min_index_val]
            velocity_max = self.v[max_index_val]

            # x0 --> self.interpolation_input_windspeed['min']
            # x1 --> self.interpolation_input_windspeed['max']
            # x  --> wsp_val

            # Angle of Attack
            # a0 --> self.alpha[min_index_val][i]
            # a1 --> self.alpha[max_index_val][i]
            # Linear Interpolation formula --> y = a0(x1-x) + a1(x-x0)/x1-x0

            # Velocity
            # v0 --> self.v[min_index_val][i]
            # v1 --> self.v[max_index_val][i]
            # Linear Interpolation formula --> y = v0(x1-x) + v1(x-x0)/x1-x0

            aoa = []
            v = []
            for i in range(len(angle_of_attack_min)):
                a0 = angle_of_attack_min[i]
                a1 = angle_of_attack_max[i]
                v0 = velocity_min[i]
                v1 = velocity_max[i]
                x = wsp_val
                x0 = self.interpolation_input_windspeed['min']
                x1 = self.interpolation_input_windspeed['max']
                lin_inter_aoa = a0 * (x1-x) + a1 * (x-x0) / (x1-x0)
                aoa.append(lin_inter_aoa)
                lin_inter_v = v0 * (x1-x) + v1 * (x-x0) / (x1-x0)
                v.append(lin_inter_v)

            self.temperature = temp_val
            self.LWC = LWC_val
            self.Time_Min = Time_val
            self.aerofoil = aerofoil_class(wsp_val, self.radius, aoa, v, self.hub_height,
                                           self.temperature, self.LWC, self.input_path, self.chord, self.Time_Min)
        except:
            raise Exception

    def get_AoA_V(self, wsp_val, index_val, temp_val, LWC_val, Time_val):
        self.temperature = temp_val
        self.LWC = LWC_val
        self.Time_Min = Time_val
        self.aerofoil = aerofoil_class(wsp_val, self.radius, self.alpha[index_val], self.v[index_val],
                                       self.hub_height, self.temperature, self.LWC, self.input_path, self.chord, self.Time_Min)


class aerofoil_class(object):

    def __init__(self, windspeed, radius, aoa, vel, hub_height, temperature, LWC, file_path, chord, Time_val):
        self.Section = radius
        self.AngleofAttack = aoa
        self.Velocity = vel
        self.HubHeight = hub_height
        self.Temperature = temperature
        self.LiquidWaterContent = LWC
        self.wind_speed = windspeed
        self.chord = chord
        self.Time_Min = Time_val
        self.getting_input_value(file_path)
        self.ValuePerSection()

    def getting_input_value(self, input_file):
        try:
            fileID = open(input_file, 'r')
            filetext = fileID.read()
            fileID.close()

            fileLines = filetext.split('\n')

            for i in range(0, len(fileLines)):
                line = fileLines[i].split(',')

                if 'relative' in line[0].casefold():
                    self.relativeHumidity = line[1].lstrip()

                elif 'dorplet' in line[0].casefold():
                    self.dorpletSize = line[1].lstrip()

                elif 'title' in line[0].casefold():
                    self.title = line[1].lstrip()

                elif 'aero' in line[0].casefold():
                    self.AERO = line[1].lstrip()

                elif 'ice' in line[0].casefold():
                    self.ICE = line[1].lstrip()

                elif 'mono-disperse' in line[0].casefold():
                    self.TRAJ = line[1].lstrip()

                elif 'ncomp' in line[0].casefold():
                    self.Ncomp = line[1].lstrip()

                elif 'dels' in line[0].casefold():
                    self.Dels = line[1].lstrip()

                elif 'nupp' in line[0].casefold():
                    self.NUpp = line[1].lstrip()

                elif 'nlow' in line[0].casefold():
                    self.NLow = line[1].lstrip()

                elif 'ruff' in line[0].casefold():
                    self.Ruff = line[1].lstrip()

                elif 'traj' in line[0].casefold():
                    self.NTRAJ = line[1].lstrip()
        except:
            raise Exception

    def ValuePerSection(self):
        for i in range(len(self.AngleofAttack)):

            # Kelvin to Centegrade
            self.Temperature_Kel = self.Temperature
            self.Temperature_Cen = self.Temperature - 273.15

            # Meter to Feet
            self.HubHeight_meter = self.HubHeight
            self.HubHeight_feet = self.HubHeight * 3.28084

            # Creating windspeed folder
            wsp_location = ".\\test\\V136_TAC2_Input_Files\\windspeed_" + \
                str(self.wind_speed)
            if not path.exists(wsp_location):
                os.mkdir(wsp_location)

            # Creating Radius folder
            radius_location = wsp_location + "\\Radius_" + \
                str(int(self.Section[i] * 1000))
            if not path.exists(radius_location):
                os.mkdir(radius_location)

            try:
                f = open(".\\test\\V136_TAC2_Input_Files\\windspeed_"+str(self.wind_speed) +
                         "\\Radius_" + str(int(self.Section[i] * 1000))+"\\TAC2_INPUT.dat", "w+")

                # writing structure as mentioned in pdf
                f.write("%s \n \n" % self.title)

                f.write(
                    "%s Icing analysis (0 for icing, 1 for aerodynamic only)\n" % self.AERO)
                f.write(
                    "%s Mono-disperse droplets (0 for mono-disperse, 1 for Langmuir-D spectrum, 2 for user-defined spectrum)\n" % self.TRAJ)
                f.write(
                    "%s No ice shape output (0 for no ice shape, 1 for creation of IHB and ET3D input files)\n \n" % self.ICE)

                f.write("$TAS = %s; Airspeed, true (m/s)\n" % self.Velocity[i])
                f.write("$AOAI = %s; Initial angle of attack (degrees)\n" %
                        self.AngleofAttack[i])
                f.write("$CHORDM = %s; Aerofil chord (m)\n" %
                        self.chord[i])
                f.write("$ALTF = %s; Altitude (feet)\n" % self.HubHeight_feet)
                f.write("$ALTM = %s; Altitude (meter)\n" %
                        self.HubHeight_meter)
                f.write("$OATC = %s; Static temperature (deg. C)\n" %
                        self.Temperature_Cen)
                f.write("$VMD = %s; Droplet median diameter (microns)\n" %
                        self.dorpletSize)
                f.write("$LWC = %s; Liquid water concentration (g/m3)\n" %
                        self.LiquidWaterContent)
                f.write("$TIME = %s; Encounter time (minutes)\n \n" %
                        self.Time_Min)

                f.write("%s \n" % self.Ncomp)
                f.write("%s \n" % self.Dels)
                f.write("%s \n" % self.NUpp)
                f.write("%s \n" % self.NLow)
                f.write("%s \n" % self.Ruff)
                f.write("%s \n" % self.NTRAJ)
                f.close()
            except:
                print("Error")
