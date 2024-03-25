#!/bin/bash

KITTY="/usr/local/kitty/kitty/launcher/kitty"

DEBUG=0
LOG_RPC=0
LAUNCHED=1
USE_RIGOL=1
USE_PIPWMM=1
SHOW_CAMERA=1
CAMERA_DEVICE=4
PIPWM_PORT=34962
CAMERA_PORT=33761
TEXTUAL_PORT=33962
CONFIG_FILE="window.conf"
TEXTUAL_TITLE="TextWindow"
CAMERA_TITLE="CameraWindow"
CAMERA_CMD="python -m tgutui camera_window"
TEXTUAL_CMD="python -m tgutui textual_window"

RIGOL_IP="127.0.0.1"
RIGOLFILE="$HOME/rigolip.txt"
if test -f "$RIGOLFILE"; then
    RIGOL_IP=`cat $RIGOLFILE`
fi

PIPWM_IP="127.0.0.1"
PIPWMFILE="$HOME/pipwmip.txt"
if test -f "$PIPWMFILE"; then
    PIPWM_IP=`cat $PIPWMFILE`
fi

export CAMERA_CMD=$CAMERA_CMD
export TEXTUAL_CMD=$TEXTUAL_CMD
export TEXTUAL_TITLE=$TEXTUAL_TITLE
export CAMERA_DEVICE=$CAMERA_DEVICE
export CAMERA_TITLE=$CAMERA_TITLE
export TEXTUAL_PORT=$TEXTUAL_PORT
export CAMERA_PORT=$CAMERA_PORT
export SHOW_CAMERA=$SHOW_CAMERA
export USE_RIGOL=$USE_RIGOL
export RIGOL_IP=$RIGOL_IP
export PIPWM_PORT=$PIPWM_PORT
export USE_PIPWM=$USE_PIPWM
export PIPWM_IP=$PIPWM_IP
export LAUNCHED=$LAUNCHED
export LOG_RPC=$LOG_RPC
export DEBUG=$DEBUG

HOLD=""
if test -f $DEBUG==1; then
    HOLD="--hold"
fi
$KITTY --title $CAMERA_TITLE --config $CONFIG_FILE --dump-commands $HOLD --detach $CAMERA_CMD