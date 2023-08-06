#!/bin/bash
set -x

>~/autocomplete_debug.log; PROGNAME=./linsharecli TEST_ARGS='--aaaaal' _ARC_DEBUG=1 COMP_LINE="$PROGNAME $TEST_ARGS" COMP_POINT=31 _ARGCOMPLETE=1 $PROGNAME 8>&1  9>>~/autocomplete_debug.log  1>>~/autocomplete_debug.log 

