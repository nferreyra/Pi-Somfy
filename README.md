# Pi-Somfy

Based on https://github.com/Nickduino/Somfy_Remote

It's a script to open and close your Somfy (and SIMU) blinds using the RTS (or Hz) protocol with a Raspberry Pi and an RF emitter. Your emitter has to use the 433.__42__ MHz frequency; the simplest might be to use a common 433.93 MHz one and to swap its oscillator for a 433.42 MHz one bought separetely.

The script will use pigpiod daemon to open and close Somfy (or SIMU) blinds.
The remote address and rolling code (incremented every time you send a frame) are stored in a specific file for every remote.

Usage
````
# somfy.py [-h] --blind BLIND --action {up,down,stop,prog}

# python somfy.py --blind 1 --action down
````

