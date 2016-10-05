#!/usr/bin/python3
from time import sleep
from datetime import datetime
from random import random
import requests
import sys

##################### Constants ############################
# These will change for each hardware setup
BME280ADDRESS = ''
DATAFILENAME  = 'exampleData.csv'
THINGSPEAKURL = 'https://api.thingspeak.com/update'
THINGSPEAKKEY = '483ZMRMW59WGBBL0'
############################################################

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

def tranThingSpeak(url, key, event, data):
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
        
def writeData(fileName, event, date, data):
    # Open a file new or existing ready to write at the end of the file.
    with open(fileName, mode='a', encoding='utf-8') as dataFile:
        #check for new file and write the header if needed
        if( dataFile.tell() < 2 ):
            dataFile.write( "Initiated "
                            + date.strftime("%Y-%m-%d, %H:%M:%S") + ", "
                            + "Date Y-M-D, Time H:M:S, "
                            + "Temp C, "
                            + "Pres. kPa, "
                            + "Humidity % "
                            + "\n")
        # write the event number and date.time to the line.
        dataFile.write( str(event)                            + ", "
                        + date.strftime("%Y-%m-%d, %H:%M:%S") + ", ")
        # Add each data element with , delimination
        for value in data:      
            dataFile.write("{:.2f} , ".format(value) )
        # end the line after all the data
        dataFile.write( "\n" )  
    #file closes as we finish the loop.
    
def main():
    # Set the event counter to one each time we start the process
    event = 1
    try:
        while True:
            # wait for the desired clock time to act
            while datetime.now().minute%5 > 0:
                sleep(60)
            # Try to read the data from the sensors
            currentData = simBME280Read()
            currentDate = datetime.now()
            # Print data to screen, and update 
            print( "\rRecorded "
                   + currentDate.strftime("%Y-%m-%d, %H:%M:%S") + " "
                   + str(currentData)
                   + "         ",
                   end=' ', flush=True)
            
            # save data on the screen by adding a new line to the overwrite
            if currentDate.minute%15 == 0:
                print(' ', end='\n', flush=True)
            # Write Data to local file
            if currentDate.minute%15 == 0:
                writeData(DATAFILENAME, event, currentDate, currentData)
            # Send data to IoT repository for storage. Later
            if currentDate.minute%15 ==0:
                tranThingSpeak(THINGSPEAKURL, THINGSPEAKKEY, event, currentData)
            # Update event count and wait before reading the current time again.
            event += 1
            sleep(60)
    except KeyboardInterrupt:
        print("Thanks for monitoring the weather."
              + "A keyboard interrupt closed the program.")
    finally:
        pass

if __name__ == '__main__':
    main()




