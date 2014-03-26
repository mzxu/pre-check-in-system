'''
Created on Jul 27, 2012

@author: Mingze
'''
import logging, os
import config

def init_logging ():
    if config.log.has_key("location"):
        logdir = config.log["location"]
    else:
        logdir = os.path.join( os.getcwd(), "logs" )
        
    loglevel = config.log["level"]
    
    if not os.path.isdir(logdir):
        os.mkdir( logdir, 0755 );
    logfile = os.path.join( logdir, "cvproxy.log" )
#    logging.basicConfig( filename=logfile, level=loglevel )
#    logfile = "/usr/local/workspace/svn-hook.log"
    logger = logging.getLogger()
    logger.setLevel( loglevel )
    # create console handler and set level to debug
    ch = logging.FileHandler(logfile)
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - {%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter( formatter )
    # add ch to logger
    logger.addHandler( ch )
    logger.setLevel(loglevel)
    return logger
    logging.DEBUG
log = init_logging()

