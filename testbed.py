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
print("Month name is {}".format(monthNames[monthIndex-1]))
print(style.available)



