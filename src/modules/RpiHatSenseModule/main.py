#    Copyright (c) 2022
#    Author      : Bruno Capuano
#    Create Time : 2022 March
#    Change Log  :
#       – Init Azure IoT module
#       – Read environmental variables
#       – Trigger telemetry message using sensehat sensors including temperature, humidity and pressure
#       – Read twin properties
#       – On twin properties patch received, show message on sensehat led display
# 
#    The MIT License (MIT)
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#    THE SOFTWARE.

import asyncio
import sys
import asyncio
import time
import threading

# Azure IoT imports
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message

# Azure IoT utils
from AzureIoTLogger import AzureIoTLogger
from AzureIoTEnvironment import AzureIoTEnvironment

# SenseHat module 
from sense_hat import SenseHat

async def main_app():
    global module_client, counter_interval, trigger_enabled
    i = 0
    AzureIoTLogger.Log(f"running eternal loop if interval > 0. Current Value: {counter_interval}")
    while (counter_interval > 0):
        i += 1
        AzureIoTLogger.Log(f"app loop {i} - ci: {counter_interval}")
        if ( i > counter_interval):
            AzureIoTLogger.Log(f"app reset {i} - ci: {counter_interval}")
            i = 0

        if (trigger_enabled == True):
            temperature = sense.get_temperature()
            temperature = round(temperature, 1)
            humidity = sense.get_humidity()
            humidity = round(humidity, 1)
            pressure = sense.get_pressure()
            pressure = round(pressure, 1)

            await send_iot_message_environmentState(temperature, humidity, pressure)

        await asyncio.sleep(counter_interval)


async def initSenseHat():
    global sense, green, red, blue, white

    AzureIoTLogger.Log( "init sense-hat" )
    sense = SenseHat()
    green = (0, 255, 0)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    white = (255, 255, 255)

    sense.clear(green)
    time.sleep(1)
    sense.clear(blue)
    time.sleep(1)
    sense.clear((0,0,0))

# =============================================
# Azure IoT
# =============================================
twin_callbacks = 0
def twin_patch_receive_messages():
    global twin_callbacks
    global module_client
    global counter_interval
    global read_twin_sleep_interval

    # Define behavior for receiving twin desired property patches
    def twin_patch_handler(twin_patch):
        try:
            AzureIoTLogger.Log ("Twin patch received - loops : %d\n" % twin_callbacks )
            AzureIoTLogger.Log (twin_patch)

            message = twin_patch["message"]
            colour = twin_patch["colour"]
            AzureIoTLogger.Log (f" New Message : {message} in '{colour}'")

            # convert string to colour
            if ( colour == "green"):
                colour = green
            elif ( colour == "red"):
                colour = red
            elif ( colour == "blue"):
                colour = blue
            else:
                colour = white

            # validate message is not an empty string
            if (len(message) > 0):
                sense.show_message(message, text_colour=colour)
                time.sleep(5)
                sense.clear((0,0,0))

        except Exception as ex:
            AzureIoTLogger.Log ( "Unexpected error in twin_patch_handler: %s" % ex )

    while True:
        try:
            # Set handlers on the client
            module_client.on_twin_desired_properties_patch_received = twin_patch_handler
            twin_callbacks += 1
            time.sleep(read_twin_sleep_interval)

        except Exception as ex:
            AzureIoTLogger.Log ( "Unexpected error in twin_patch_listener: %s" % ex )


async def initAzureIoTModule():
    global module_client, read_twin_sleep_interval, trigger_enabled, counter_interval
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        AzureIoTLogger.Log( "IoT Hub Client for Python !" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # read environmental vars
        trigger_enabled = AzureIoTEnvironment.GetEnvVarBool('ReportValues')
        counter_interval = AzureIoTEnvironment.GetEnvVarInt('CounterInterval')
        read_twin_sleep_interval = AzureIoTEnvironment.GetEnvVarInt('ReadTwinSleepInterval')
        if ( read_twin_sleep_interval <= 0):
            read_twin_sleep_interval = 5        

        # connect the client.
        await module_client.connect()
        AzureIoTLogger.Log ( "The Azure IoT Edge Module is now waiting for messages. ")

    except Exception as e:
        AzureIoTLogger.Log ( "Unexpected error %s " % e )
        raise

async def send_iot_message_environmentState(temperature, humidity, pressure):
    # send iot messages
    # send message reference https://docs.microsoft.com/en-us/python/api/azure-iot-device/azure.iot.device.aio.iothubmoduleclient?view=azure-python#send-message-message-

    global module_client, trigger_enabled

    try:
        if (trigger_enabled == True):
            AzureIoTLogger.Log("start send message")

            MSG_TXT = '{{"temperature": "{temperature}","humidity": "{humidity}","pressure": "{pressure}"}}'
            msg_txt_json_formatted = MSG_TXT.format(temperature=temperature, humidity=humidity, pressure=pressure)
            message = Message(msg_txt_json_formatted)
            message.custom_properties['temperature'] = temperature
            message.custom_properties['humidity'] = humidity
            message.custom_properties['pressure'] = pressure
            AzureIoTLogger.Log( message )
            await module_client.send_message(message)
            
            AzureIoTLogger.Log("message sent")
    except Exception as e:
        AzureIoTLogger.Log(e)
        return 'Error sending IoT message', 500        

async def update_device_state(temperature, humidity, pressure):
    global module_client    
    try:    
        # send telemetry messages        
        await send_iot_message_environmentState(temperature, humidity, pressure)

        # update twin properties
        reported_patch = {"temperature": temperature}
        module_client.patch_twin_reported_properties(reported_patch)
        reported_patch = {"humidity": humidity}
        module_client.patch_twin_reported_properties(reported_patch)
        reported_patch = {"pressure": pressure}
        module_client.patch_twin_reported_properties(reported_patch)

    except Exception as e:
        AzureIoTLogger.Log ( "update_device_state - Unexpected error %s " % e )
        raise

if __name__ == "__main__":
#    main()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initAzureIoTModule())
    loop.run_until_complete(initSenseHat())    

    # new thread to read twin values
    stateThread = threading.Thread(target=twin_patch_receive_messages)
    stateThread.daemon = True   
    stateThread.start()

    loop.run_until_complete(main_app())    

    #loop.close()
