#!/bin/bash

if [ -z "$1" ]; then

    python -m hermes
    #python -m hermes hermes/webcam_surveillance

else

    python -m hermes
    # ipython -m hermes hermes/webcam_surveillance

fi
