import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import subprocess
from datetime import timedelta, datetime, tzinfo, timezone

local_timezone = "Europe/Prague"
data_path = "/home/vojtech/web.kotek.co/data/"
static_path = "/home/vojtech/web.kotek.co/myapp/static/"
days_delta = 7

def get_data():

    # Copy latest sql and csv data from RPi (rpi.kotek.co)
    try:
        subprocess.check_call([data_path + "getData.sh"], shell=True, stdout=True)
    except Exception as e:
        print("Failed getting data..", str(e))

def load_data():

    # INTERNET
    internet_temp = pd.DataFrame(pd.read_csv(data_path+"data_internet.csv"))
    internet = pd.DataFrame()
    internet['timestamp'] = pd.to_datetime(internet_temp['Timestamp']).dt.tz_localize('UTC').dt.tz_convert(local_timezone)
    internet['latency'] = internet_temp['Ping']
    internet['download'] = internet_temp['Download'] * 1e-6
    internet['upload'] = internet_temp['Upload'] * 1e-6

    # TEMPERATURE
    db = sqlite3.connect(data_path+"data_climate.db")
    sql_query = "SELECT * FROM data"
    climate = pd.read_sql_query(sql_query, db)
    climate['timestamp'] = pd.to_datetime(climate['time']).dt.tz_localize('UTC').dt.tz_convert(local_timezone)
    climate.set_index('timestamp')
    climate['temperature_rolling'] = climate['temperature'].rolling(6).mean()
    climate['humidity_rolling'] = climate['humidity'].rolling(6).mean()

    # SNAPSHOT
    status = """CLIMATE @ {}\n\tTemperature: \t{}C \n\tHumidity: \t{}%
        \nINTERNET @ {}\n\tDown/Up: \t{}/{} Mbps \n\tLatency: \t{} ms""".format(
        climate.iloc[-1]['timestamp'],
        climate.iloc[-1]['temperature'],
        climate.iloc[-1]['humidity'],
        internet.iloc[-1]['timestamp'],
        round(internet.iloc[-1]['download'], 1),
        round(internet.iloc[-1]['upload'], 1),
        round(internet.iloc[-1]['latency'], 1),
        )

    data = {'climate': climate, 'internet': internet }

    response = {'status': status,
                'data': data }

    return response

#### CanvasJS data export functions ####

def get_climate_daily():

    db = sqlite3.connect(data_path+"data_climate.db")
    sql_query = """SELECT DATE(time) AS date,
                ROUND(AVG(temperature),1) AS temperature,
                ROUND(AVG(humidity),1) AS humidity
                FROM data
                WHERE date > DATE('now', '-1 year')
                GROUP BY date"""
    temp = pd.read_sql_query(sql_query, db)
    temp = [list(row) for row in temp.itertuples()]
    db.close()

    return temp

def get_climate():

    db = sqlite3.connect(data_path+"data_climate.db")
    sql_query = """SELECT DATETIME(time) AS time,
                ROUND(temperature,1) AS temperature,
                ROUND(humidity,1) AS humidity
                FROM data
                """
    data = pd.read_sql_query(sql_query, db)
    db.close()
    return data

def update_graphs():

    end = datetime.now()
    start = (end - timedelta(days=days_delta))

    plt.figure(figsize=(15,15))

    # INTERNET

    ## Up/Down
    plt.subplot(311)
    plt.title('Internet Speed and Latency')
    plt.grid(True)
    plt.plot(internet['Time'], internet['Up'], '.', label='Upload')
    plt.plot(internet['Time'], internet['Dwn'], '.', label='Download')
    plt.legend()
    plt.ylabel('Speed (Mb)')
    plt.xlim(start, end)

    ## Latency
    plt.subplot(312)
    plt.grid(True)
    plt.xlabel('Date')
    plt.ylabel('Ping (ms)')
    plt.plot(internet['Time'], internet['Png'], '.', label='Ping (ms)')
    plt.legend()
    plt.ylim(0, 100)
    plt.xlim(start, end)

    # CLIMATE

    plt.subplot(313)
    plt.title('Room Temperature & Humidity (30m running avg.)')
    plt.grid(True)
    plt.plot(climate['time'], climate['temperature_rolling'], '.', label='Temperature (C)')
    plt.plot(climate['time'], climate['humidity_rolling'], '.', label='Humidity (%)')
    plt.legend()
    plt.ylabel('Value')
    plt.xlim(start, end)

    filename = "data_graphs.png"

    plt.savefig(static_path+filename)

    return filename

def update_all():
    try:
        print('Getting data..', end="")
        get_data()
        print('OK!')
#        print('Loading data..', end="")
#        load_data()
#        print('OK!')
#        print('Updating graphs..', end="")
#        update_graphs()
#        print('Skipped')
    except:
        return False
    print('Done!')
    return True
