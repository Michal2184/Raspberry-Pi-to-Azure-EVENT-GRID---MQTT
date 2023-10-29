"""
Raspberry Pi to Azure MQTT CLient - Publish + Subscribe
Uses Self Signed SSL cert for authentication.

i2c devices:
AHT20 and 0.91 OLED display

"""
import board
import busio
import adafruit_ahtx0
import paho.mqtt.client as mqtt
from time import sleep
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont


class IoTDevice:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
        self.sensor = adafruit_ahtx0.AHTx0(board.I2C())
        self.status = True
        self.broker_hostname = "vhome-mqtt.northeurope-1.ts.eventgrid.azure.net"
        self.port = 8883
        self.client = mqtt.Client("client1-authnid")
        self.client.username_pw_set(username="client1-authnid")
        self.client.tls_set(certfile="./client1-authnID.pem",
                            keyfile="./client1-authnID.key")
        self.topicsPub = ["RPi/Sensors/temp", "RPi/Sensors/humi"]
        self.topicsSub = ["RPi/Input/led1", "RPi/Input/led2", "RPi/Input/relay1"]
        self.mqttConStatus = "OFF"
        # pins
        self.led1status = False
        self.led2status = False
        self.relay1status = False
        self.relay2status = False

    def start(self):
        # Establish connection to Azure
        print("Connection to Azure in Progress...")
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker_hostname, self.port)
        for i in range(len(self.topicsSub)):
            self.client.subscribe(self.topicsSub[i])
        self.client.on_message = self.on_message
        # leave 5 sec for a handshake to compleate
        sleep(3)
        self.client.loop_start()
        self.oled.fill(0)
        # Main loop
        while self.status:
            try:
                # collect values from sensors and format
                temp = round(self.sensor.temperature, 4)
                humi = round(self.sensor.relative_humidity, 4)
                # publish valeus to topics
                self.client.publish("RPi/Sensors/temp", temp)
                self.client.publish("RPi/Sensors/humi", humi)
                # update screen
                self.oled.show()
                self.rederDisplay(temp, humi)
                print(f"Payload: {temp} , {humi}")
                # reduce sending frequency
                sleep(10)
            except KeyboardInterrupt:
                self.rederDisplay(temp="---", humi="---", off=True)
                self.client.loop_stop()
                break
        # stop client service after status change
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, return_code):
        if return_code == 0:
            print("Connected to Azure...OK")
            self.mqttConStatus = "AZURE CONNECTION: ON"
        else:
            print("Could not connect to Azure...", return_code)
            self.mqttConStatus = "AZURE CONNECTION: OFF"

    def rederDisplay(self, temp="---", humi="---", off=False):
        # Create blank image for drawing.
        image = Image.new("1", (self.oled.width, self.oled.height))
        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        # Generate text
        tempText = f"TEMP: {temp} *C"
        (font_width, font_height) = font.getsize(tempText)
        draw.text((0, 0), tempText, font=font, fill=255)
        tempText = f"HUMI: {humi} %"
        draw.text((0, 10), tempText, font=font, fill=255)
        # connction status
        if not off:
            tempText = "AZURE CONNECTION: ON"
        else:
            tempText = "AZURE CONNECTION: OFF"
        draw.text((0, 23), tempText, font=font, fill=255)
        # Display image
        self.oled.image(image)
        self.oled.show()

    def on_message(self, client, userdata, msg):
        """ react to messages subscribed to """
        valueReceived = int(msg.payload.decode())
        topicReceived = msg.topic
        print(f"Received: {valueReceived} from {topicReceived}")
        if topicReceived =="RPi/Input/led1":
            self.togglePin(1, valueReceived)
        elif topicReceived == "RPi/Input/led2":
            self.togglePin(2, valueReceived)
        elif topicReceived == "RPi/Input/relay1":
            self.togglePin(3, valueReceived)
    
    def togglePin(self, ledNum, received):
        """ turning LED on of depending on the argument received """
        # LED 1
        if ledNum == 1:
            if received:
                if self.led1status:
                    print(f"LED1: Already ON")
                else:
                    # Turn ON    
                    self.led1status = True
                    print(f"LED1: ON")
            else:
                if not self.led1status:
                    print(f"LED1: Already OFF")
                else:
                    # Turn OFF    
                    self.led1status = False
                    print(f"LED1: OFF")
        # LED 2
        elif ledNum == 2:
            if received:
                if self.led2status:
                    print(f"LED2: Already ON")
                else: 
                    # Turn ON   
                    self.led2status = True
                    print(f"LED2: ON")
            else:
                if not self.led2status:
                    print(f"LED2: Already OFF")
                else:
                    # Turn OFF    
                    self.led2status = False
                    print(f"LED2: OFF")
        
        elif ledNum == 3:
            if received:
                if self.relay1status:
                    print(f"Relay 1: Already ON")
                else: 
                    # Turn ON   
                    self.relay1status = True
                    print(f"Relay 1: ON")
            else:
                if not self.relay1status:
                    print(f"Relay 1: Already OFF")
                else:
                    # Turn OFF    
                    self.relay1status = False
                    print(f"Relay 1: OFF")

if __name__ == "__main__":
    """ RUN CLIENT """
    x = IoTDevice()
    x.start()
