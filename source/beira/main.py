
# -*- coding: utf-8 -*-

__author__ = "Diogo Samora Cerqueira (DISCE)"
__copyright__ = "(c)2019 Vestas Technology R&D"
__version__ = "0.0.0"


from os import path
import os
from tkinter import Tk
from tkinter import filedialog
import pandas
import numpy
from .utils import is_number
from .geometry import blade_class, aerofoil_class


class beira_class(object):

    def __init__(self, inputFilepath):

        print('Initialising beira\n')
        # initialise Beira simulation class
        self.reset()

        self.inputFilepath = inputFilepath

        # Read the input file and CSV file to get the Wind speed and pyro input and output files
        self.readInput(self.inputFilepath)

        self.blade = blade_class(self.solver, self.bladeInp, self.bladeOut, self.vasLayout,
                                 self.bladeSectionFolder, self.weatherTable, self.inputFilepath, self.timeScheme)
        print('Beira initialisation complete')

    def reset(self):
        # reset Beira simulation class
        self.blade = []
        self.solver = ''
        self.bladeInp = ''
        self.bladeInp = ''
        self.timeScheme = ''
        self.weatherfile = ''
        self.bladeSectionFolder = ''
        self.vasLayout = []
        self.simulation = ''
        self.weatherTable = []
        self.relativeHumidity = None
        self.dorpletSize = None

    def readInput(self, inputFile):

        self.reset()

        if inputFile != '':
            if inputFile[0] == '"':
                inputFile = inputFile[1:len(inputFile)]
            if inputFile[len(inputFile)-1] == '"':
                inputFile = inputFile[0:len(inputFile)-1]

        if not path.exists(inputFile):
            raise Exception("Input file not found")

        fileID = open(inputFile, 'r')
        filetext = fileID.read()
        fileID.close()

        fileLines = filetext.split('\n')

        for i in range(0, len(fileLines)):
            line = fileLines[i].split(',')

            if 'sim' in line[0].casefold():
                if 'heat' in line[1].casefold():
                    self.simulation = 'heatflux'

            if 'solver' in line[0].casefold():
                if 'pyro' in line[1].casefold():
                    self.solver = 'pyro'

            elif 'bladeinp' in line[0].casefold():
                self.bladeInp = line[1].lstrip()

            elif 'bladeout' in line[0].casefold():
                self.bladeOut = line[1].lstrip()

            elif 'relative' in line[0].casefold():
                self.relativeHumidity = line[1].lstrip()

            elif 'dorplet' in line[0].casefold():
                self.dorpletSize = line[1].lstrip()

            elif 'weather' in line[0].casefold():
                self.loadWeather(line[1].lstrip())

            elif 'bladesectionsfolder' in line[0].casefold():
                self.bladeSectionFolder = line[1].lstrip()

            elif 'minradius' in line[0].casefold():
                for j in range(1, len(line)):
                    line[j] = line[j].strip()
                columns = line

                table = []

                i = i+1
                line = fileLines[i].split(',')
                while is_number(line[0]):
                    table.append(line)
                    i = i+1
                    if i > len(fileLines):
                        break
                    line = fileLines[i].split(',')

                self.vasLayout = pandas.DataFrame(table, columns=columns)

    def loadWeather(self, weatherfile):

        # load weather cases
        print("Reading CSV")
        abs_path = path.dirname(path.abspath(__file__))
        abs_path_rstrip = path.dirname(abs_path.rstrip('/'))
        weatherfile = path.join(abs_path_rstrip, weatherfile)
        self.csv_data = pandas.read_csv(weatherfile)
        self.weatherTable = self.validate_wsp(self.csv_data)

    def validate_wsp(self, wsp):
        weather_table_json = {}
        weather_table_json['wsp'] = []
        weather_table_json['temp'] = []
        weather_table_json['lwc'] = []
        weather_table_json['time'] = []

        wsp_array = numpy.array(wsp.WSP100)
        temperature_array = numpy.array(wsp.TK100)
        lwc_array = numpy.array(wsp.LWC)
        time_array = numpy.array(wsp.Time_Min)

        weather_table_json['wsp'] = wsp_array
        weather_table_json['temp'] = temperature_array
        weather_table_json['lwc'] = lwc_array
        weather_table_json['time'] = time_array

        for wsp_val in wsp.WSP100:
            numpy_array = numpy.array(wsp.WSP100)
            indexval = numpy_array.tolist().index(wsp_val)

            if wsp.Time_Min[indexval] == 0.0 or wsp.Time_Min[indexval] < 0.0:
                weather_table_json['wsp'] = numpy.delete(
                    wsp_array, indexval, axis=0)
                weather_table_json['temp'] = numpy.delete(
                    temperature_array, indexval, axis=0)
                weather_table_json['lwc'] = numpy.delete(
                    lwc_array, indexval, axis=0)

        return weather_table_json

    def heatflux(self):
        print('Heat Flux simulation started')
        print("heat Flux simulation completed")

    def run(self):

        self.heatflux()
        print("simulation completed")
