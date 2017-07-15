#!/bin/bash

if [ -z "$1" ]; then

    python -m hermes hermes/webcam_surveillance

else

    ipython -m hermes hermes/webcam_surveillance

fi
