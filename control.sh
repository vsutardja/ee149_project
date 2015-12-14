#!/bin/bash

if [[ -n "$1" ]]; then
    IP="$1"
else
    IP="192.168.2.9"
fi

if [[ -n "$2" ]]; then
    PORT="$2"
else
    PORT=1234
fi

KOBUKI="admin@$IP"

scp -r "${KOBUKI}:img/" .
exit

ssh "$KOBUKI" '~/kobukiNavigation' &
python thresholding.py
python spline.py
