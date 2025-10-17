#!/bin/bash

# name of usb device
CAMERA_NAME="USB Camera: USB Camera"

OUTPUT=$(v4l2-ctl --list-devices)

echo "==============================="
echo "$OUTPUT"
echo "==============================="
echo

DEVICE=$(echo "$OUTPUT" | awk -v cam="$CAMERA_NAME" '
    $0 ~ cam {getline; print $1; exit}
')

if [ -z "$DEVICE" ]; then
    echo "❌ Error: no device with name '$CAMERA_NAME'"
    exit 1
fi

DEV_NUM=${DEVICE#/dev/video}

echo "✅ Found device: $DEVICE (Nr: $DEV_NUM)"
echo
echo "🚀 Start: python3 main.py --device $DEV_NUM"
python3 main.py --device "$DEV_NUM"
