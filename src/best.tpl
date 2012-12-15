#!/bin/sh

# if this script was run through condor there is a return from XDS
# if it exists: 
if [ ! -z "$$2" ]
then
    if [ "$$2" -ne "0" ]
    then
    	# Error code > 0
    	echo "Job $$1 return the error code $$2 : Best will not be executed "
    	exit 1
    fi    	
fi

# otherwise runs best normally
export besthome=$besthome

$bestbin -f $detector -t $exposure_time  -Bonly \
-o $folder/best.mtv \
-dna $folder/best.xml \
-xds $folder/CORRECT.LP \
$folder/BKGINIT.cbf \
$folder/XDS_ASCII.HKL  \
> $folder/best.log 2>&1


