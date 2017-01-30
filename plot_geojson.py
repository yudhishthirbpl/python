import requests
import json
import configparser as cp
import datetime as dt
import time as t


class GeoJsonContext:
    __context=None
    __properties_file_name=None

    def __init__(self, properties_file_name):
        self.__properties_file_name=properties_file_name

    def get_usgs_context(self):
        if self.__context == None:
            self.__context = cp.RawConfigParser()
            self.__context.read(self.__properties_file_name)
            return self.__context
        else:
            return self.__context


class GeoJSONDict:
    """
    Class GeoJSONDict encapsulates python dict data structure.
    In this module GeoJSON class is used to create subset of JSON response
    received from USGS API.
    GeoJSON object encapsulates data dict format i.e. {'key1':[],'key2':[]}
    so that it can be directly used to create visualizations and plots using pandas and matplotlib
    """
    __masterDataFrame = {}
    __columnNames = ("type","alert","mag","time","depth","id","felt","longitude","latitude")

    def __init__(self):
        self.__masterDataFrame = {column_name: [] for column_name in self.__columnNames}


    def set_type(self,type):
        (self.__masterDataFrame['type']).append(type)

    def set_alert(self,alert):
        (self.__masterDataFrame['alert']).append(alert)

    def set_magnitude(self,magnitude):
        (self.__masterDataFrame['mag']).append(magnitude)

    def set_time(self,timeObj):
        if timeObj == None:
            dtObj = dt.datetime.fromtimestamp(int(t.time()))
            (self.__masterDataFrame['time']).append(dtObj)
        else:
            epochTS = float(timeObj) / 1000
            dtObj = dt.datetime.fromtimestamp(int(epochTS))
            (self.__masterDataFrame['time']).append(dtObj)

    def set_depth(self,depth):
        (self.__masterDataFrame['depth']).append(depth)

    def set_id(self,id):
        (self.__masterDataFrame['id']).append(id)

    def set_felt(self, felt):
        if felt != None:
            (self.__masterDataFrame['felt']).append(int(felt))
        else:
            (self.__masterDataFrame['felt']).append(int("0"))

    def set_longitude(self, longitude):
        if longitude != None:
            (self.__masterDataFrame['longitude']).append(float(longitude))
        else:
            (self.__masterDataFrame['longitude']).append(float("0.0"))

    def set_latitude(self, latitude):
        if latitude != None:
            (self.__masterDataFrame['latitude']).append(float(latitude))
        else:
            (self.__masterDataFrame['latitude']).append(float("0.0"))

    def get_masterdataframe(self):
        return self.__masterDataFrame


#main() method
def main():
   geo_json_context = create_context()
   end_date = dt.datetime.fromtimestamp(int(t.time()))
   start_date = end_date + dt.timedelta(days=-365)
   usgs_geojson_url = create_usgs_call_url(geo_json_context.get(geo_json_context.sections()[0],'usgs_geojson_api_url')
                                            , "{}-{}-{}".format(start_date.year, start_date.month, start_date.day)
                                            , "{}-{}-{}".format(end_date.year, end_date.month, end_date.day) ,3)

   parse_geojson(fetch_data_from_usgs(usgs_geojson_url),geo_json_context)

   try:
       pass
   except:
       pass
   else:
       pass
   finally:
       pass



def create_context(properties_file_name="config.properties"):
    return GeoJsonContext(properties_file_name).get_usgs_context()

def create_usgs_call_url(usgs_api_url="https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={}&endtime={}&minmagnitude={}",
                         start_date="2016-01-01", end_date="2016-12-31",
                         min_magnitude=3):
    return usgs_api_url.format(start_date,end_date,min_magnitude)


def fetch_data_from_usgs(usgs_call_url="https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2016-01-01&endtime=2016-12-31&minmagnitude=3"):
    return requests.get(usgs_call_url)


def parse_geojson(response, geo_json_context):
    features_list = [response.json()[geojson_key] for geojson_key in response.json().keys() if geojson_key == geo_json_context.get(geo_json_context.sections()[0],'features_key_name')]
    index=0
    for feature in features_list:
        index=index+1
        print("index = {}".format(index))










#Entry Point
if __name__ == '__main__':
    """"
    Execute main() method only when plot_geojson.py is executed directly using
    python i.e. python plot_geojson.py
    """
    main()





#def create_geojson_call_url(start_date="{}-{}-{}".(), end_date, min_magnitude):