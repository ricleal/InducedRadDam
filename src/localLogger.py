
import os
import sys
import logging
import logging.config

import ini


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING'  : YELLOW,
    'INFO'     : GREEN,
    'DEBUG'    : BLUE,
    'CRITICAL' : YELLOW,
    'ERROR'    : RED,
    'RED'      : RED,
    'GREEN'    : GREEN,
    'YELLOW'   : YELLOW,
    'BLUE'     : BLUE,
    'MAGENTA'  : MAGENTA,
    'CYAN'     : CYAN,
    'WHITE'    : WHITE,
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ  = "\033[1m"


class ColorFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        color     = COLOR_SEQ % (30 + COLORS[levelname])
        message   = logging.Formatter.format(self, record)
        message   = message.replace("$RESET", RESET_SEQ)\
                           .replace("$BOLD",  BOLD_SEQ)\
                           .replace("$COLOR", color)
        for k,v in COLORS.items():
            message = message.replace("$" + k,    COLOR_SEQ % (v+30))\
                             .replace("$BG" + k,  COLOR_SEQ % (v+40))\
                             .replace("$BG-" + k, COLOR_SEQ % (v+40))
        return message + RESET_SEQ

class LocalLogger :
    """
    Initialises Logger
    """
    
    def __init__(self,name = None) :
        # Configure logging
        
        self.logConfFileName = ini.Ini().getParTestFile("GENERAL","log_conf_file")
        
        logging.ColorFormatter = ColorFormatter        
        
        logging.config.fileConfig(self.logConfFileName)

        # create logger
        if name == None :
            self.logger = logging.getLogger()
        else :
            self.logger = logging.getLogger(name)



if __name__ == "__main__":
    lr = LocalLogger()
    
    lr.logger.debug("debug message")
    lr.logger.info("info message")
    lr.logger.warn("warn message")
    
    lp = LocalLogger("processing")
    lp.logger.error("error message")
    lp.logger.critical("critical message")

    