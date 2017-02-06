import requests
import json
import configparser as cp
import datetime as dt
import time as t
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from pandas.tools.plotting import scatter_matrix
import folium as fl


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


class MyGeoJson:
    """
    Class MyGeoJson encapsulates python dict data structure.
    In this module GeoJSON class is used to create subset of JSON response
    received from USGS API.
    GeoJSON object encapsulates data dict format i.e. {'key1':[],'key2':[]}
    so that it can be directly used to create visualizations and plots using pandas and matplotlib
    """
    __masterDataFrame = {}
    __columnNames = ("type", "alert", "mag", "time", "depth", "id", "felt", "longitude", "latitude", "sig", "nst", "place")

    def __init__(self):
        self.__masterDataFrame = {column_name: [] for column_name in self.__columnNames}

    def set_type(self,type):
        (self.__masterDataFrame['type']).append(type)

    def set_alert(self,alert):
        if alert is None:
            (self.__masterDataFrame['alert']).append('green')
        else:
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

    def set_sig(self,sig):
        (self.__masterDataFrame['sig']).append(sig)

    def set_place(self, place):
        (self.__masterDataFrame['place']).append(place)

    def set_nst(self,nst):
        if nst is None:
            (self.__masterDataFrame['nst']).append(int('0'))
        else:
            (self.__masterDataFrame['nst']).append(nst)

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
   my_geojson = None

   try:
       geojson_context = create_context()
       end_date = dt.datetime.fromtimestamp(int(t.time()))
       start_date = end_date + dt.timedelta(days=-365)
       usgs_geojson_url = create_usgs_call_url(
           geojson_context.get(geojson_context.sections()[0], 'usgs_geojson_api_url')
           , "{}-{}-{}".format(start_date.year, start_date.month, start_date.day)
           , "{}-{}-{}".format(end_date.year, end_date.month, end_date.day), 3)

       feature_data_list = parse_geojson(fetch_data_from_usgs(usgs_geojson_url), geojson_context)
       my_geojson = populate_my_geojson(feature_data_list, geojson_context)
   except Exception as exception:
       print("Something went wrong while retrieving data from USGS Site. Error is {}".format(exception))
   else:
       df = pd.DataFrame(my_geojson.get_masterdataframe())

       column_names = ['felt', 'mag', 'depth', 'sig', 'nst']
       mag_felt_df = df.loc[:, column_names]
       # Correlation between felt, mag, depth, sig and nst
       plot_correlation(mag_felt_df, column_names)

       # Histogram
       #plot_histogram(mag_felt_df)

       # Plot Map using Folium
       # plot_map(df, 'usgs_mag_6.html')
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


def parse_geojson(geojson_response, geojson_context):
    features_list = [geojson_response.json()[geojson_key] for geojson_key in geojson_response.json().keys()
                     if geojson_key == geojson_context.get(geojson_context.sections()[0],'features_key_name')]

    feature_data_list = []
    if len(features_list) == 1:
        feature_data_list = [feature_data_dict for feature_data_dict in features_list[0]]
    else:
        raise ValueError("Invalid data structure found in geojson. Size of features list is {}".format(len(features_list)))

    return feature_data_list


def populate_my_geojson(feature_data_list, geojson_context):
    my_geojson = MyGeoJson()
    if feature_data_list is None:
        raise ValueError("feature_data_list is None. Can't proceed ahead in method: {}".format('populate_my_geojson'))
    for feature_data_dict in feature_data_list:
        if feature_data_dict is None:
            continue
        my_geojson.set_id(feature_data_dict[geojson_context.get(geojson_context.sections()[0],'features_id_key_name')])
        my_geojson = populate_my_geojson_properties(geojson_context, my_geojson,
                                                    feature_data_dict[geojson_context.get(geojson_context.sections()[0],
                                                                                          'properties_key_name')])
        my_geojson = populate_my_geojson_geometry(geojson_context, my_geojson,
                                                  feature_data_dict[geojson_context.get(geojson_context.sections()[0],
                                                                                        'geometry_key_name')])
    return my_geojson


def populate_my_geojson_properties(geojson_context, my_geojson, properties_data_dict):
    if properties_data_dict is None:
        raise ValueError("properties_data_dict is None. Can't proceed ahead in method: {}".format('populate_my_geojson_properties'))
    my_geojson.set_alert(properties_data_dict[geojson_context.get(geojson_context.sections()[0],'properties_alert_key_name')])
    my_geojson.set_type(properties_data_dict[geojson_context.get(geojson_context.sections()[0],'properties_type_key_name')])
    my_geojson.set_magnitude(properties_data_dict[geojson_context.get(geojson_context.sections()[0],'properties_magnitude_key_name')])
    my_geojson.set_time(properties_data_dict[geojson_context.get(geojson_context.sections()[0],'properties_time_key_name')])
    my_geojson.set_felt(properties_data_dict[geojson_context.get(geojson_context.sections()[0],'properties_felt_key_name')])
    my_geojson.set_sig(properties_data_dict[geojson_context.get(geojson_context.sections()[0], 'properties_sig_key_name')])
    my_geojson.set_nst(properties_data_dict[geojson_context.get(geojson_context.sections()[0], 'properties_nst_key_name')])
    my_geojson.set_place(properties_data_dict[geojson_context.get(geojson_context.sections()[0], 'properties_place_key_name')])
    return my_geojson


def populate_my_geojson_geometry(geojson_context, my_geojson, geometry_data_dict):
    if geometry_data_dict is None:
        raise ValueError("geometry_data_dict is None. Can't proceed ahead in method: {}".format('populate_my_geojson_geometry'))
    my_geojson.set_longitude((geometry_data_dict[geojson_context.get(geojson_context.sections()[0],'geometry_coordinates_key_name')])[0])
    my_geojson.set_latitude((geometry_data_dict[geojson_context.get(geojson_context.sections()[0],'geometry_coordinates_key_name')])[1])
    my_geojson.set_depth((geometry_data_dict[geojson_context.get(geojson_context.sections()[0],'geometry_coordinates_key_name')])[2])
    return my_geojson

def plot_correlation(mag_felt_df, column_names):
    correlations = mag_felt_df.corr()
    fig = plt.figure()
    ax = fig.add_subplot(2, 3, 4)
    cax = ax.matshow(correlations, vmin=-1, vmax=1)
    fig.colorbar(cax)
    ticks = np.arange(0, 5, 1)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels(column_names)
    ax.set_yticklabels(column_names)
    style.use('seaborn-poster')
    plt.show()

def plot_histogram(mag_felt_df):
    mag_felt_df.hist()
    style.use('seaborn-poster')
    plt.show()


def plot_map(df, plot_file_name):
    map = fl.Map(location=[df['latitude'].mean(), df['longitude'].mean()], tiles='Mapbox bright', zoom_start=6)
    fg = fl.FeatureGroup(name='earthquake locations')
    for index, row in df.iterrows():
        fg.add_child(fl.Marker(location=[row['latitude'], row['longitude']], popup=fl.Popup(row['place']),
                               icon=fl.Icon(color=row['alert'])))

    map.add_child(fg)
    map.save(outfile=plot_file_name)


#Entry Point
if __name__ == '__main__':
    """"
    Execute main() method only when plot_geojson.py is executed directly using
    python i.e. python plot_geojson.py
    """
    main()





