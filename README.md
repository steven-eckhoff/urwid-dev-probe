# Urwid Dev Probe

![Logo](https://github.com/steven-eckhoff/urwid-dev-probe/blob/master/logo.jpg)

## History

This is a project I started because I needed a simple tool that would allow me
to peek and poke I2C devices. I also wanted to make a tool that was very
straight forward when it came to adding support for additional devices and
adapters. Hopefully, this could reduce the number of tools out there that do the
same thing for different devices.

At this point, this is just a prototype of a much more polished tool. What I
envision is that someone could take this an either find the device and adapter
already supported or be able to add support very easily with some config files
and some simple middleware. I chose Urwid because it is lightweight and simple
to use.


## Status

**This project is currently in the *hacky* phase.** Despite this, it is useful to
those with a Bus Pirate and an I2C device that they need to probe.


## Install

    $ sudo apt-get install python3-pip
    $ sudo pip3 install urwid
    $ sudo pip3 install pyserial


## Run

    $ cd <DIRECTORY_WITH_MAIN_PY>
    $ python3 main.py


## Use

1. Once you are in the GUI select a device that you want to probe

2. Once you have selected your device, select the adapter that you are using.
Currently Bus Pirate is the only one.

3. Now you can go to the device page and you will see all the registers that
were defined in the config file. You can read/write an individual register by
pressing the corresponding buttons for the register. You can also use the global
read/write operations, which will do bulk read/write for all the registers with
their checkboxes enabled.

## TODO

1. Decouple GUI from read/write operations with threads

2. Register coalescing for bulk read/writes

3. A much better GUI. Maybe allow users to pick their own ugly colors through a 
config file.

4. Add another adapter and evaluate how the current architecture will work with 
adding new adapters and devices.
