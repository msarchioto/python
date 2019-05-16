#####################################################
# Author: Michele Sarchioto                         #
# Date: 2019-05-14                                  #
# Project: Test Fatturazione                        #
# Description: Billing projects for Vayu            #
# File: main.py                                     #
# File Desc: start up logger, args and worker class #
#####################################################

import fatturazione
import argparse
import sys
import logging
from logging import handlers

sysError = 1
fileNotSpecifiedError = 3

def createNewLogger():

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # define formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logFileName = __file__.split('.py')[0] + '.log'
    logHandler = handlers.TimedRotatingFileHandler(logFileName, when='D', interval=1, backupCount=2)
    logHandler.setLevel(logging.INFO)
    # set logHandler's formatter
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    return logger

# Main function - take input from sys argv (input) and pass it to fatturazione Class
def main():

    try:
        # define logger
        logger = createNewLogger()
        logger.info('Process Start')

        # parse input arguments
        parser = argparse.ArgumentParser(description='Process input file and config file')
        parser.add_argument('--inputfile', type=str, help='input file name')
        parser.add_argument('--conf', type=str, help='config file name')

        args = parser.parse_args()

        # check arguments
        if args.inputfile is None or args.inputfile == '':
            # file not specified
            logger.error('Parameter "inputfile" not specified, try to "python main.py -h" for help')
            # return system error, file not specified
            return sys.exit(fileNotSpecifiedError)
        else:
            logger.info('Starting Fatturazione with the following parameters:')
            logger.info('Input file - {}'.format(args.inputfile))
            logger.info('Config file - {}'.format(args.conf))
            # create instance of class Fatturazione
            fattWorker = fatturazione.Fatturazione(args.inputfile, args.conf, logger)
            returnError = fattWorker.run()

            # Check output error and file name
            if returnError is not None:
                logger.error('Error while processing file: {}'.format(returnError['error']))
            else:
                logger.info('Output file name: {}'.format(fattWorker.outputFileName))

            logger.info('Ending Fatturazione process')

    except Exception as e:
        # handle unexpected script errors
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Exception while running main() function: {} - line {}'.format(e, exc_tb.tb_lineno))
        # return system error
        return sys.exit(sysError)

# Main
if __name__ == '__main__':

    main()
