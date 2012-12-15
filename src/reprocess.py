#!/usr/bin/env python2.6

"""

This file will simulate the autoindexserver


run as :  /opt/pxsoft/tools/python/v2.6.6/redhate4-x86_64/bin/python \
            /bliss/users/leal/Python/AutoInducedRadDam/src/reprocess.py -e EDApplication_20101126-094937 \
            -p 'xds_t1w?_run1_1' -s 1 -f 21

in : process folder


-e <edna folder>
-p <xds template>, e.g.: 'xds_t1w?_run1_1'
-s <start from>, default 1
-f <last one>, default 21
-t <step>, default 2


"""

import time
import os
import sys

import sys
import getopt

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "he:p:s:f:t:", ["help", "edna=", "path=", "start=", "finish=", "step="])
        except getopt.error, msg:
            raise Usage(msg)

        start = '1'
        end = '21'
        step = 2
        
        # option processing
        for option, value in opts:
            if option in ("-h", "--help"):
                raise Usage(__doc__)
            if option in ("-e", "--edna"):
                edna = value
            if option in ("-p", "--path"):
                path = os.getcwd() + '/' + value
            if option in ("-s", "--start"):
                start = value
            if option in ("-f", "--finish"):
                end = value                 
            if option in ("-t", "--step"):
                step = int(value)
         
    except Usage, err:
        print >>sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >>sys.stderr, "     for help use --help"
        return 2

    
    #pathPattern = os.getcwd() + '/xds_tp1w?_run1_1'
    
    if step == 1 :
        #commandStr = 'InducedRadDam.py -e %s -p %s -f %s'
        # for debugging
        #commandStr = 'export PATH=$PATH:/opt/pxsoft/tools/python/v2.6.6/redhate5-x86_64/bin/python; /opt/pxsoft/tools/python/v2.6.6/redhate5-x86_64/bin/python /mntdirect/_bliss/users/leal/Python/AutoInducedRadDam/src/main.py -e %s -p %s -l %s'
        commandStr = '/bliss/users/leal/Python/InducedRadDam/src/InducedRadDam.py -e %s -p %s -l %s'
        
    else :
        #commandStr = 'InducedRadDam.py -i -e %s -p %s -f %s'
        # for debugging
        commandStr = '/bliss/users/leal/Python/InducedRadDam/src/InducedRadDam.py -i -e %s -p %s -l %s'
    
    
    for i in range(int(start),int(end)+1,step) :
        folder = path.replace('?',str(i))
        command = commandStr % (edna,folder,end)
        print command
        ret = os.system(command)
        if ret is not 0:
            sys.exit(1)
        time.sleep(0)
    
    print "Simulation finished......"

    
    

if __name__ == "__main__":
    sys.exit(main()) 












