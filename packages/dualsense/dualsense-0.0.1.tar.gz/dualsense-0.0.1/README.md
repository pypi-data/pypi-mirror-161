# Dualsense PS5 Controller Interface

This module provides a clean-ish, reasonably high-speed interface to a PS5 'DualSense' controller. 
It has fewer features than other libraries that provide similar functionality, `pydualsense` for example, but is more performant in my experience and perhaps easier to use.

## Requirements

Only works on Linux or FreeBSD (not tested).
Tested on a raspberrypi

## Installation

`pip install .` should work just fine

## Usage

Find a controller connected to the system with `DualSenseController.find_controller()`
This object will then update itself at a high frequency as long as the coroutine `arun` is, well... running
