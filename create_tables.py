"""Code for creating the database data.db and for creating the tables of
the database: light1,...,light4 (light measurement tables for each BEST lab
sensor number) and cloud (weather data from Wunderground).
"""

import sqlite3
from sqlite3 import dbapi2 as sqlite3

#Create a database data.db and connect to it
connection = sqlite3.connect('data.db')
cursor = connection.cursor()


#Create one table for cloud measurement data

cursor.execute('''CREATE TABLE cloud (timezone TEXT, year INTEGER, month
                INTEGER, day INTEGER, hour INTEGER, minute INTEGER, seconds
                INTEGER, unixtime REAL, cloudiness TEXT, cloudvalue REAL, daycloudvalue REAL,PRIMARY KEY
                (year, month, day, hour, minute, seconds))''')


#Create one table per sensor for light measurement data
cursor.execute('''CREATE TABLE light1 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL, exponential REAL, average REAL,
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE light2 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL, exponential REAL, average REAL,
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE light3 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL, exponential REAL, average REAL,
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE light4 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL, exponential REAL, average REAL,
                PRIMARY KEY (unixtime))''')

#Light tables for NASA

cursor.execute('''CREATE TABLE nasalight1 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL,
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE nasalight2 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL,
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE nasalight3 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL,
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE nasalight4 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL,
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE nasalight5 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL,
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE nasalight6 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL,
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE nasalight7 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL,
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE nasalight8 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL, 
                PRIMARY KEY (unixtime))''')

cursor.execute('''CREATE TABLE nasalight9 (unixtime REAL, weekday TEXT,
                day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                azimuth REAL, cloudiness TEXT, x REAL, y REAL, error2_1 REAL,
                error2_2 REAL, error5_1 REAL, error5_2 REAL, error10_1 REAL,
                error10_2 REAL, 
                PRIMARY KEY (unixtime))''')

#Create one table per model based on sensor number, # of bins, and sunangle
#degree angle


cursor.execute('''CREATE TABLE model2 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')

cursor.execute('''CREATE TABLE model3 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')

cursor.execute('''CREATE TABLE model4 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
               ''')



cursor.execute('''CREATE TABLE nasamodel1 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')

cursor.execute('''CREATE TABLE nasamodel2 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')
cursor.execute('''CREATE TABLE nasamodel3 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')
cursor.execute('''CREATE TABLE nasamodel4 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')

cursor.execute('''CREATE TABLE nasamodel5 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')

cursor.execute('''CREATE TABLE nasamodel6 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')

cursor.execute('''CREATE TABLE nasamodel7 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')

cursor.execute('''CREATE TABLE nasamodel8 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')

cursor.execute('''CREATE TABLE nasamodel9 (sunangle REAL, cloudiness TEXT, sunexposure TEXT,
                coefficient2_1 REAL, constant2_1 REAL, rsquared2_1 REAL,
                coefficient2_2 REAL, constant2_2 REAL, rsquared2_2 REAL,
                coefficient5_1 REAL, constant5_1 REAL, rsquared5_1 REAL,
                coefficient5_2 REAL, constant5_2 REAL, rsquared5_2 REAL,
                coefficient10_1 REAL, constant10_1 REAL, rsquared10_1 REAL,
                coefficient10_2 REAL, constant10_2 REAL, rsquared10_2 REAL)
                ''')

#Save your changes
connection.commit()
