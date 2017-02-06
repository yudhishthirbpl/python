import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import time as t
import matplotlib.pyplot as plt
from matplotlib import style


"""
Scratch pad for testing python functions and APIs
"""

dtObj = dt.datetime.fromtimestamp(int(t.time()))
monthNames = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")
monthIndex = dtObj.month
#print("Month name is {}".format(monthNames[monthIndex-1]))
#print(style.available)

num_list = [1,2,3,4,5,6,7,8,9,10]

#list comprehension
square_of_nums = [num*num for num in num_list if (num*num)%9 == 0]
#for num in num_list
#    square_of_nums.append(num*num)

#print(square_of_nums)
#Range
#print(range(2016,2017))

#datetime
my_date = dt.datetime.now()
#print(my_date.strftime("%b"))
#http://strftime.org/
my_new_date = my_date + dt.timedelta(days=-30)
#print("my_new_date = {}".format(my_new_date))

months_name_list = []

my_temp_date = None

for i in range(12):
    if i == 0:
        my_temp_date = my_date + dt.timedelta(days=-30)
    else:
        my_temp_date = months_name_list[i-1]+ dt.timedelta(days=-30)

    months_name_list.append(my_temp_date)

#print(months_name_list)
#"{}-{}".format(my_temp_date.strftime('%b'),my_temp_date.year)
x_axis_label = ["{}-{}".format(temp_date.strftime('%b'),temp_date.year) for temp_date in months_name_list]
#print(x_axis_label)

#

my_list = [(letter,num) for letter in 'abcd' if letter!='a' for num in range(4) if num%2 == 0]
print(my_list)

rs = np.random.RandomState(33)
print(rs.normal(size=(100, 26)))


import folium
#folium.Map(location=[45.5236, -122.6750])
#map_osm.create_map(path='osm.html')

