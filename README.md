# Raspberry-Pi-to-Azure-EVENT-GRID---MQTT

Project made to test the possibility of sending data to SCADA systems over the internet using AZURE. One of the most fastest option was to utilize AZURE EVENT GRID and its build in MQTT broker. 
Great results was achieved on one of the mainstream SCADA systems as they all now support MQTT

Raspberry PI was equipped with:
- AHT20 Temperature and Humidity 
- 0.91 OLED Display
- 2x Relays for voltage switching
- 2x LEDs

  Paho MQTT library was used for this project

Create ceritificates using Azure Documentation: 
https://learn.microsoft.com/en-us/azure/event-grid/mqtt-certificate-chain-client-authentication
