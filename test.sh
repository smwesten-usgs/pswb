#!/bin/sh

NXNY="120 430"

NX=$(echo $NXNY | awk '{print $1}' )
NY=$(echo $NXNY | awk '{print $2}' )

echo $NX, $NY