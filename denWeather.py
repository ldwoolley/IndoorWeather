#!/usr/bin/env python3
from time import sleep
from datetime import datetime
from random import random
import requests
import logging
from Adafruit_BME280 import BME280

 
##################### Constants ############################
# These will change for each hardware setup
BME280_I2CADDR = 0x76
BME280_OSAMPLE_8 = 4
DATAFILENAME  = 'data-denWeather.csv'
LOGFILENAME = 'log-denWeather.log'
UBIDOTSTOKEN  = '5pGTL4RDWCTAGToq8izKe5gp7oVQrU'
UBIDOTSURL = 'https://things.ubidots.com/api/v1.6/devices/denweather/'
THINGSPEAKURL = 'https://api.thingspeak.com/update'
THINGSPEAKKEY = '483ZMRMW59WGBBL0'
############################################################

logging.basicConfig(level=logging.INFO, filename=LOGFILENAME,
                    format='%(asctime)s, %(levelname)s, '
                           '%(module)s, %(message)s')

def read_bme280(sensor):
    """Query the BME280 sensor and return [temp C, pres. kPa, hum. %]"""
    try:
        degrees = round(sensor.read_temperature(), 2)
        kpascals = round(sensor.read_pressure()/1000, 3)
        humidity = round(sensor.read_humidity(), 2)
        return [degrees, kpascals, humidity]
    except:
        log.exception('BME280 read failed')
        raise


def sim_bme280_read():
    """Simulate the output of read_bme280(sensor) with changing data"""
    data = [20.0, 101.0, 50.0 ]
    return [round(value+(5-10*random()),2) for value in data]


def tran_ubidots(url, token, data):
    """Transmit data to Ubidots using requests.post"""
    # format the total url.
    posturl = url + "?token=" + token
    # TODO(Lance): update for generic data payload length.
    payload = {"temperature": data[0], "pressure": data[1], "humidity": data[2]}
    # Transmit data, allow other actions even if this one has a common error.
    try:
        req = requests.post( posturl, payload)
    except requests.exceptions.HTTPError as error:
        logging.exception('Ubidots POST failed')
    except requests.exceptions.ConnectionError as error:
        logging.exception('Ubidots POST failed')
    except requests.exceptions.Timeout as error:
        logging.exception('Ubidots POST failed')
    except requests.exceptions.TooManyRedirects as error:
        logging.exception('Ubidots POST failed')
    except requests.exceptions.RequestException as error:
        # Catastrophic error. bail
        logging.exception('Ubidots POST failed')
        raise error
    else:
        pass
    finally:
        pass
        

def tran_thing_speak(url, key, data):
    """Transmit data to ThingSpeak using requset.post"""
    # Build the TingSpeak payload 
    payload = {'api_key': key,}
    for index, value in enumerate(data[:8], start=1):
        payload['field{}'.format(index)]='{:.2f}'.format(value)
    # Transmit data, allow other actions even if this one has a common error.
    try:
        req = requests.post( url, params=payload)
    except requests.exceptions.HTTPError as error:
        logging.exception('ThingSpeak POST failed')
    except requests.exceptions.ConnectionError as error:
        logging.exception('ThingSpeak POST failed')
    except requests.exceptions.Timeout as error:
        logging.exception('ThingSpeak POST failed')
    except requests.exceptions.TooManyRedirects as error:
        logging.exception('ThingSpeak POST failed')
    except requests.exceptions.RequestException as error:
        # Catastrophic error. bail
        logging.exception('ThingSpeak POST failed')
        raise error
    else:
        pass
    finally:
        pass
        

def write_data(name, date, data):
    """Write CSV data to new or existing file, allow other process if file write failes."""
    try:
        with open(name, mode='a', encoding='utf-8') as data_file:
            #Write a header label if this is a new file.
            if(data_file.tell() < 2 ):
                data_file.write("Initiated "
                                + date.strftime("%Y-%m-%d, %H:%M:%S") + ", "
                                + "\n")
                data_file.write("Date Y-M-D, Time H:M:S, "
                                + "Temp C, "
                                + "Pres. kPa, "
                                + "Humidity % "
                                + "\n")
            # write date, time, then each data item to the line.
            data_file.write(date.strftime("%Y-%m-%d")   + ", "
                            + date.strftime("%H:%M:%S") + ", ")
            for value in data:      
                data_file.write("{:.2f} , ".format(value) )
            data_file.write("\n")  
        #file closes as we finish the loop.
    except (IOError, OSError) as error:
        log.exception('There was a file exception')
    else:
        pass
    finally:
        pass


def main():
    """This program reads from a Bosch BME280 sensor over i2c and then
       sends the results to the screen, a file, ubidots, and thingspeak
       Using datetime.now() to trigger activity on whole minute or hours
       while displaying a running clock updated on the second."""
    logging.info('Starting the program')
    try:
        sensor = BME280(mode=BME280_OSAMPLE_8, address=BME280_I2CADDR)
        while True:
            current_date = datetime.now()
            # On each whole minute check if it should read and record the data
            if current_date.second == 0:
                if current_date.minute%10 == 0:
                    current_data = read_bme280(sensor)
                    # record the data on the screen, file and websites
                    print( "\rRecord  "
                           + current_date.strftime("%Y-%m-%d %H:%M:%S") + " "
                           + str(current_data)
                           + "         ",
                           end=' \n', flush=True)
                    write_data(DATAFILENAME, current_date, current_data)
                    tran_thing_speak(THINGSPEAKURL, THINGSPEAKKEY, current_data)
                    tran_ubidots(UBIDOTSURL, UBIDOTSTOKEN, current_data)
                    logging.info('Collected/Saved {}'.format(current_data))
            # Update the current datetime line each second 
            print( "\rWaiting "
                   + current_date.strftime("%Y-%m-%d %H:%M:%S") + " ",
                   end=' ', flush=True)
            sleep(0.5)
    except KeyboardInterrupt:
        logging.exception('The KeyboardInterrupt will stop the program')
    finally:
        logging.info('Enging the program')

if __name__ == '__main__':
    main()




