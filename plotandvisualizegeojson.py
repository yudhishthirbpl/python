"""
This module illustrates how to leverage popular python objects (i.e. datetime, requests, matplotlib etc.)
and data structures (i.e. list, dict, dataframes, pandas and custom class) to call JSON based
rest web service and carry out some basic data visulization and plotting operations
:Author: Yudhishthir Kaushik <yudhishthirbpl@hotmail.com>
build on python 3.5.2 Anaconda distribution
"""

# Imports section
# All necessary Imports will be places here
# Issue: os and json modules are required on ubuntu. On Windows code worked fine without these imports also.

import requests
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import time as t
from matplotlib import style



# --------------- Master Data Frame Object to store processed JSON Response  (start)
class GeoJSONDict:
    """
    Class GeoJSONDict encapsulates python dict data structure.
    In this module GeoJSON class is used to create subset of JSON response
    received from USGS API.
    GeoJSON object encapsulates data dict format i.e. {'key1':[],'key2':[]}
    so that it can be directly used to create visulization and plots using pandas and matplotlib
    """
    __masterDataFrame = {}
    __columnNames = ("type","alert","mag","place","time","depth","id")

    def __init__(self):
        #Initialize the Master Data Frame with Keys and Empty Lists
        for columnName in self.__columnNames:
            self.__masterDataFrame[columnName] = []

    def setType(self,type):
        (self.__masterDataFrame['type']).append(type)

    def setAlert(self,alert):
        (self.__masterDataFrame['alert']).append(alert)

    def setMag(self,mag):
        (self.__masterDataFrame['mag']).append(mag)

    def setPlace(self,place):
        (self.__masterDataFrame['place']).append(place)

    def setTime(self,timeObj):
        if timeObj == None:
            dtObj = dt.datetime.fromtimestamp(int(t.time()))
            (self.__masterDataFrame['time']).append(dtObj)
        else:
            epochTS = float(timeObj) / 1000
            dtObj = dt.datetime.fromtimestamp(int(epochTS))#Not sure what would be the impact of missing tz >>> Todo
            (self.__masterDataFrame['time']).append(dtObj)

    def setDepth(self,depth):
        (self.__masterDataFrame['depth']).append(depth)

    def setId(self,id):
        (self.__masterDataFrame['id']).append(id)

    def getMasterDataFrame(self):
        return self.__masterDataFrame
# --------------- Master Data Frame Object to store processed JSON Response  (End)

# --------------- Util functions for processing JSON Response Object (Start)

def processProperties(properties,geoJSONDict):

    """
    returns updated geoJSON object
    processProperties() : Function to process Properties dict object retrieved from GeoJSON
    param: properties - dict object
    param: geoJSON - object of GeoJSON class
    """
    if properties == None:
        raise " Properties object is Null, can't proceed ahead !!!! for recordId={} ".format(recordId)
    geoJSONDict.setAlert(properties[PROPERTIES_ALERT_KEY_NAME])
    geoJSONDict.setType(properties[PROPERTIES_TYPE_KEY_NAME])
    geoJSONDict.setMag(properties[PROPERTIES_MAG_KEY_NAME])
    geoJSONDict.setPlace(properties[PROPERTIES_PLACE_KEY_NAME])
    geoJSONDict.setTime(properties[PROPERTIES_TIME_KEY_NAME])
    return geoJSONDict

def processGeometry(geometry,geoJSONDict):
    """
    returns updated geoJSON object
    processGeometry() : Function to process Geometry dict object retrieved from GeoJSON
    param: geometry - dict object
    param: geoJSON - object of GeoJSON class
    """
    if (geometry == None) and (geometry[GEOMETRY_COORDINATES_KEY_NAME] == None):
        raise " Geometry > Coordinates object is Null, can't proceed ahead !!!! for recordId={} ".format(recordId)
    geoJSONDict.setDepth((geometry[GEOMETRY_COORDINATES_KEY_NAME])[2])#Within coordinates, depth value is avaialble at index=3 in the list
    return geoJSONDict
# --------------- Util functions for processing JSON Response Object (End)


#To handle null values in GeoJSON response
null = "null"
#Lower control limit for earthquake magnitude. Value of this variable will be used to filter data coming from USGS API
MAGNITUDE_LCL = 6
'''
URL for accessing USGS data Services
For now I am keeping the URL hardcoded but this can be dynamically creatd using datetime object
starttime yyyy-mm-dd endtime yyyy-mm-dd
minmagnitude >= MAGNITUDE_LCL
'''
urldtObj = dt.datetime.fromtimestamp(int(t.time()))

USGS_WS_API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2016-01-01&endtime={}-{}-{}&minmagnitude={}".format(urldtObj.year,urldtObj.month,urldtObj.day,MAGNITUDE_LCL)
print("In finally block. Program Started at {} ".format(dt.datetime.fromtimestamp(t.time())))
print("REST API URL is {}".format(USGS_WS_API_URL))
#Global Variables
#constants
#Todo:can be configured through properties file or db ??? for better maintainability
FEATURES_KEY_NAME = "features"
FEATURES_ID_KEY_NAME = "id"
GEOMETRY_KEY_NAME = "geometry"
PROPERTIES_KEY_NAME = "properties"
PROPERTIES_ALERT_KEY_NAME = "alert"
PROPERTIES_TYPE_KEY_NAME = "type"
PROPERTIES_MAG_KEY_NAME = "mag"
PROPERTIES_PLACE_KEY_NAME = "place"
PROPERTIES_TIME_KEY_NAME = "time"
GEOMETRY_COORDINATES_KEY_NAME = "coordinates"


#Transaction Variables
GeoJSONResponse = {}
keys = []
Features = []
Properties = {}
Geometry = {}
recordId = None
geoJSONDict = GeoJSONDict()


# Main section .... where processing will be done
try:
    GeoJSONResponse = requests.get(USGS_WS_API_URL)
    #Checking whether GeoJSONResponse is Dictionary object or not
    """
    key ==> features, type ==> <class 'list'>
    key ==> type, type ==> <class 'str'>
    key ==> metadata, type ==> <class 'dict'>
    key ==> bbox, type ==> <class 'list'>
    """

    if isinstance(GeoJSONResponse.json(), dict):
        keys = GeoJSONResponse.json().keys()
    for key in keys:
        if (key == None):
            continue
        if (isinstance(GeoJSONResponse.json()[key],list)) and (key == FEATURES_KEY_NAME):
            features = GeoJSONResponse.json()[key]
            if(features == None):
                continue
            for feature in features:
                if feature == None:
                    continue
                recordId = feature[FEATURES_ID_KEY_NAME]
                if(recordId != None):
                      geoJSONDict.setId(recordId)
                else:
                    print(" ....... recordID is None ..... ")
                    continue

                Properties = feature[PROPERTIES_KEY_NAME]
                if Properties == None:
                    continue
                else:
                    geoJSONDict = processProperties(Properties,geoJSONDict)
                Geometry = feature[GEOMETRY_KEY_NAME]
                if Geometry == None:
                    continue
                else:
                    geoJSONDict = processGeometry(Geometry,geoJSONDict)
except Exception as exception:
    print("Something went wrong while retrieving data from USGS Site. Error is {}".format(exception))
else:
    #Placeholder for code to generate plots using matplotlib.pyplot with by using dataframes and Pandas (if possible)
    df = pd.DataFrame(geoJSONDict.getMasterDataFrame())
    #print(df)
    #df.set_index("id",inplace='true')#setting dataframe index to "id" column
    #style.use('classic')
    #(df.head(10))['mag'].plot()#Generating plot for first 100 'mag' data values. In the similar way plat can be generated for other columns also.
    #plt.ylabel("Magnitude")
    #plt.xlabel("Event ID")
    #plt.show()

    monthNames = ("Jan-2016", "Feb-2016", "Mar-2016", "Apr-2016", "May-2016", "Jun-2016", "Jul-2016", "Aug-2016", "Sep-2016", "Oct-2016", "Nov-2016", "Dec-2016","Jan-2017")
    monthlyCountList =  []
    monthWiseCountDict = {'Months':[],'Count':[]}#Initializing monthWiseCountDict data structure
    for monthName in monthNames:
        if monthName == None:
            continue
        monthlyTotal = 0
        for index, row in df.iterrows():
            dtObj = row['time']
            if dtObj == None:
                continue
            if (monthName == monthNames[dtObj.month-1]) and (dtObj.year != 2017):
                monthlyTotal = monthlyTotal + 1
            elif (dtObj.year == 2017) and (dtObj.month == 1):#Special Handling for Jan-2017 records
                monthlyTotal = monthlyTotal + 1

        (monthWiseCountDict['Months']).append(monthName)
        (monthWiseCountDict['Count']).append(monthlyTotal)

    """
    The following lines of code will create plot which will illustrate
    the total no of Earthquake events where magnitude >= 6 registered by USGS for the perid
    starting from 2016-01-01 to till date i.e. 13 months approx.
    """
    megDF = pd.DataFrame(monthWiseCountDict)
    megDF.set_index('Months',inplace='true')
    style.use('seaborn-bright')
    megDF.plot()
    plt.xlabel('Months')
    plt.ylabel('#earthquakes/month with magnitude >= {}'.format(MAGNITUDE_LCL))
    plt.xticks([0,1,2,3,4,5,6,7,8,9,10,11,12],monthWiseCountDict['Months'])
    plt.show()

finally:
    print("In finally block. Program culminated at {} ".format(dt.datetime.fromtimestamp(t.time())))

