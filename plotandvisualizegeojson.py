"""
This module illustrates how to leverage popular python objects (i.e. datetime, requests, matplotlib etc.)
and data structures (i.e. list, dict, dataframes, pandas and custom class) to call JSON based
rest web service and carry out some basic data visulization and plotting operations
:Author: Yudhishthir Kaushik <yudhishthirbpl@hotmail.com>
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

    def setTime(self,time):
        if time == None:
            time = (int(t.time()))*1000
        epochTS = float(time) / 1000
        dtObj = dt.datetime.fromtimestamp(int(epochTS))#Not sure what would be the impact of missing tz >>> Todo
        (self.__masterDataFrame['time']).append("{}-{}-{}".format(dtObj.year,dtObj.day,dtObj.month))

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
'''
URL for accessing USGS data Services
#For now I am keeping the URL hardcoded but this can be dynamically creatd using datetime object
'''
USGS_WS_API_URL = "http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2016-01-01&endtime=2016-01-12"


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
    '''
    key ==> features, type ==> <class 'list'>
    key ==> type, type ==> <class 'str'>
    key ==> metadata, type ==> <class 'dict'>
    key ==> bbox, type ==> <class 'list'>
    '''
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
    pass
    #Placeholder for code to generate plots using matplotlib.pyplot with by using dataframes and Pandas (if possible)
    df = pd.DataFrame(geoJSONDict.getMasterDataFrame())
    df.set_index("time",inplace='true')#setting dataframe index to "time" column
    style.use('fivethirtyeight')
    (df.head(100))['mag'].plot()#Generating plot for first 100 'mag' data values. In the similar way plat can be generated for other columns also.
    plt.ylabel("Magnitude")
    plt.show()
finally:
    print(" In finally block. Program culminated at {} ".format(dt.datetime.fromtimestamp(t.time())))

