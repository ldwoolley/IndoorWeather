#!/usr/bin/python3
from time import sleep
from datetime import datetime
from random import random
import requests
import sys
from Adafruit_BME280 import BME280

##################### Constants ############################
# These will change for each hardware setup
BME280ADDRESS = ''
DATAFILENAME  = 'exampleData.csv'
THINGSPEAKURL = 'https://api.thingspeak.com/update'
THINGSPEAKKEY = '483ZMRMW59WGBBL0'
UBIDOTSTOKEN  = '5pGTL4RDWCTAGToq8izKe5gp7oVQrU'
UBIDOTSURL = 'https://things.ubidots.com/api/v1.6/devices/denweather/'
############################################################

# call the sensor to read the specific data
def readBME280( sensor ):
    degrees = round(sensor.read_temperature(), 2)
    kpascals = round(sensor.read_pressure()/1000, 2)
    humidity = round(sensor.read_humidity(), 2)

    return [ degrees, kpascals, humidity ]

# function to simulate call to data source
def simBME280Read():
    try:
        data = [ 20.0, 101.0, 50.0 ]
        data = [ round(value+(5-10*random()),2) for value in data]
        #print(data, flush=True)
        return data
    except KeyboardInterrupt:
        print("Thanks for monitoring the weather."
              + "A keyboard interrupt closed the data read function.")
        raise KeyboardInterrupt
    finally:
        #clean up the GPIO
        #print("The GPIO has been closed.")
        pass

def tranUbidots(url, token, data):
    # use your API and data to establish the parameter list.
    posturl = url + "?token=" + token
    # may want to update data field to be a dictionary with the correct elements.
    payload = {"temperature": data[0], "pressure": data[1], "humidity": data[2]}
    # Define the connection setup.
    try:
        req = requests.post( posturl, payload)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        print("Could not transmit event {}.".format( event))
        print(sys.exc_info()[0])
    else:
        pass
    finally:
        pass
        
def tranThingSpeak(url, key, data):
    # use your API and data to establish the parameter list.
    payload = {'api_key': key,}
    # add field# dictionary entry for any data upto 8 (thingspeak channel limit)
    for index, value in enumerate(data[:8], start=1):
        payload['field{}'.format(index)]='{:.2f}'.format(value)
    # Define the connection setup.
    try:
        req = requests.post( url, params=payload)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        print("Could not transmit event {}.".format( event))
        print(sys.exc_info()[0])
    else:
        pass
    finally:
        pass
        
def writeData(fileName, date, data):
    # Open a file new or existing ready to write at the end of the file.
    with open(fileName, mode='a', encoding='utf-8') as dataFile:
        #check for new file and write the header if needed
        if( dataFile.tell() < 2 ):
            dataFile.write( "Initiated "
                            + date.strftime("%Y-%m-%d, %H:%M:%S") + ", "
                            + "\n")
            dataFile.write("Date Y-M-D, Time H:M:S, "
                            + "Temp C, "
                            + "Pres. kPa, "
                            + "Humidity % "
                            + "\n")
        # write the event number and date.time to the line.
        dataFile.write( date.strftime("%Y-%m-%d")   + ", "
                        + date.strftime("%H:%M:%S") + ", ")
        # Add each data element with , delimination
        for value in data:      
            dataFile.write("{:.2f} , ".format(value) )
        # end the line after all the data
        dataFile.write( "\n" )  
    #file closes as we finish the loop.

##This program checks the clock time every second and if the modulo time is whole
##then it will read the data.  If the minute module is a whole number it will
##record the data to the screen, a file, and to one or more IoT repositories.
def main():
    try:
        while True:
            sensor = BME280(mode=4)
            currentDate = datetime.now()
            # wait for the desired clock time to act
            if currentDate.second == 0:
                if currentDate.minute%15 == 0:
                    # Read the data from the sensors
                    #currentData = simBME280Read()
                    currentData = readBME280(sensor)
                    # save data on the screen by adding a new line to the overwrite
                    print( "\rRecord  "
                           + currentDate.strftime("%Y-%m-%d %H:%M:%S") + " "
                           + str(currentData)
                           + "         ",
                           end=' \n', flush=True)
                    # Write Data to local file
                    writeData(DATAFILENAME, currentDate, currentData)
                    # Send data to IoT repository for storage.
                    tranThingSpeak(THINGSPEAKURL, THINGSPEAKKEY, currentData)
                    tranUbidots(UBIDOTSURL, UBIDOTSTOKEN, currentData)

            else:
                pass
            # Print date to screen, and update 
            print( "\rWaiting "
                   + currentDate.strftime("%Y-%m-%d %H:%M:%S") + " ",
                   end=' ', flush=True)
            #Sleep a full second sleep(1)
            sleep(1)
    except KeyboardInterrupt:
        print("Thanks for monitoring the weather."
              + "A keyboard interrupt closed the program.")
    finally:
        pass

if __name__ == '__main__':
    main()




