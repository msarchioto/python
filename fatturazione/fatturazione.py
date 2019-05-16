#####################################################
# Author: Michele Sarchioto                         #
# Date: 2019-05-14                                  #
# Project: Test Fatturazione                        #
# Description: Billing projects for Vayu            #
# File: fatturazione.py                             #
# File Desc: worker class definition                #
#####################################################

import sys
import csv
import json
import datetime
from calendar import monthrange

class Fatturazione:

    # Fatturazione Init
    def __init__(self, inputFile, configFile, logger):
        # Input variables
        self.inputFile = inputFile
        self.configFile = configFile
        self.logger = logger

        # Input File Data
        self.csvFile = None
        self.inputData = None

        # Cfg file data
        self.cfgData = {}

        # Fields to process with default values that can be overwritten by the cfg file
        self.inputCols = ['NrFattura', 'DataFattura', 'ModalitaDiPagamento']
        self.outputCols = ['NrFattura', 'DataFattura', 'DataScadenzaPagamento']
        self.validModes = ["DF", "DFFM", "DF60"]
        self.idField = 'NrFattura'
        self.dateField = 'DataFattura'
        self.modeField = 'ModalitaDiPagamento'
        self.csvDelimiter = ';'

        '''
        # Lines reserved for debugging
        self.inputCols = None
        self.outputCols = None
        self.validModes = None
        self.idField = None
        self.dateField = None
        self.modeField = None
        self.csvDelimiter = None
        '''

        # function pointer to determine which function to use from the 'Modalita di Pagamento"
        self.funcPointer = {
                        'DF' : self.dfHandler,
                        'DFFM': self.dffmHandler,
                        'DF60': self.df60Handler
        }

        #output variables
        self.error = None
        self.outputData = []    # define the output as a list of array of strings, sortable
        self.outputFileName = None


    # Main Fatturazione method, opens input file and creates output
    def run(self):

        # Stage 1 - Import cfg file
        self.openCfgFile()

        # Stage 2 - Import file and save it into a variable
        self.logger.info('Stage 2 - Import file data')
        self.openInputFile()

        if self.error is not None:
            # return error message, stop execution
            self.logger.error('Error while trying to open input file')
            return self.error

        # stage 3 - Run through file and create output if there was no error in S2 and inputData has a value
        self.logger.info('Stage 3 - Parsing input and preparing output')
        self.parseInput()

        if self.error is not None:
            # return error message, stop execution
            self.logger.error('Error while trying to parse input file')
            return self.error


        # Stage 4 - Save output to file if there was no error in S3
        self.logger.info('Stage 4 - Save output to file')
        self.saveToFile()

        # return Error None
        return self.error

    # Opens config file and saves it to local variable, it will also overwrite default values if valid
    def openCfgFile(self):

        try:
            # Open config file as dictionary
            with open(self.configFile) as cfgFile:
                self.cfgData = json.load(cfgFile)

                # if not empty or null
                if self.cfgData:
                    # overwrite values if present
                    if 'inputCols' in self.cfgData:
                        self.inputCols = self.cfgData['inputCols']
                    if 'outputCols' in self.cfgData:
                        self.outputCols = self.cfgData['outputCols']
                    if 'validModes' in self.cfgData:
                        self.validModes = self.cfgData['validModes']
                    if 'idField' in self.cfgData:
                        self.idField = self.cfgData['idField']
                    if 'dateField' in self.cfgData:
                        self.dateField = self.cfgData['dateField']
                    if 'modeField' in self.cfgData:
                        self.modeField = self.cfgData['modeField']
                    if 'csvDelimiter' in self.cfgData:
                        # the str() is necessary under linux
                        self.csvDelimiter = str(self.cfgData['csvDelimiter'])
                else:
                    self.logger('Config file empty, sticking with default values')

        except Exception as e:
            # handle unexpected script errors
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.errorHandler(e, 'openCfgFile()', exc_tb.tb_lineno)


    # Opens input file and saves it to local variable
    def openInputFile(self):

        try:
            # Open file as dictionary
            # Note: A list could use less memory but a dictionary is more useful
            # if we add a new column. Also the code is more readable.
            self.csvFile = open(self.inputFile)
            fileHandler = csv.DictReader(self.csvFile, delimiter=self.csvDelimiter)
            self.inputData = [row for row in fileHandler]

            # check for empty file
            if len(self.inputData) == 0:
                self.error = {'error': 'Empty file'}

            # extract columns
            self.fileCols = fileHandler.fieldnames

            # Close file
            self.csvFile.close()
        except Exception as e:
            # handle unexpected script errors
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.errorHandler(e, 'openInputFile()', exc_tb.tb_lineno)


    # Parses the input data after the file has been loaded into a dict
    def parseInput(self):

        try:
            # check if file has the correct input columns
            checkInputColsResult = sorted(self.inputCols) == sorted(self.fileCols)

            # if the column name are as expected from the config file
            if checkInputColsResult:

                # iterate through lines
                for singleLine in self.inputData:

                    # check for correct/valid date format
                    if self.checkDate(singleLine[self.dateField]):

                        # Try to determine type
                        modeType = singleLine[self.modeField]
                        # find the handler function, if it's valid
                        if modeType in self.funcPointer and modeType in self.validModes :
                            handlerFunc = self.funcPointer[modeType]
                            handlerFunc(singleLine)
                        else:   # else write error line
                            errorMessage = 'Invalid Mode at ID {}: {}'.format(singleLine[self.idField], modeType)
                            self.logger.error(errorMessage)
                            errorLine = [singleLine[self.idField], singleLine[self.dateField], errorMessage]
                            self.outputData.append(errorLine)

                    else:   # else write error line
                        errorMessage = 'Invalid Date at ID {}: {}'.format(singleLine[self.idField], singleLine[self.dateField])
                        self.logger.error(errorMessage)
                        errorLine = [singleLine[self.idField], singleLine[self.dateField], errorMessage]
                        self.outputData.append(errorLine)

            else:   # wrong columns
                errorMessage = 'Invalid CSV Columns: {}'.format(self.fileCols)
                self.logger.error(errorMessage)
                self.error = {'error': errorMessage}

        except Exception as e:
            # handle unexpected script errors
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.errorHandler(e, 'parseInput()', exc_tb.tb_lineno)


    # Error Exception handler
    def errorHandler(self, e, funcname, line):

        message = 'Exception while running {} function: {} - line {}'.format(funcname, e, line)
        self.logger.error(message)
        # define error return
        self.error = {'error': message}


    # This handler DSP is equalt o DF
    def dfHandler(self, line):

        tempOutputLine = [line[self.idField], line[self.dateField], line[self.dateField]]
        # append to output
        self.outputData.append(tempOutputLine)


    # This handler DSP is at the end of the month
    def dffmHandler(self, line):

        # calculate last day of the month thanks to the standard library calendar
        dateFattura = line[self.dateField]
        yearTemp = dateFattura.split('-')[0]
        monthTemp = dateFattura.split('-')[1]

        lastDay = monthrange(int(yearTemp), int(monthTemp))[1]
        newDate = yearTemp + '-' + monthTemp + '-' + str(lastDay)

        tempOutputLine = [line[self.idField], line[self.dateField], newDate]
        # append to output
        self.outputData.append(tempOutputLine)


    # This handler DSP is DF + 60 days
    def df60Handler(self, line):

        newDateStr = self.addTwoMonthsToDate(line[self.dateField])

        tempOutputLine = [line[self.idField], line[self.dateField], newDateStr]
        # append to output
        self.outputData.append(tempOutputLine)


    # This method adds two months to a date
    def addTwoMonthsToDate(self, inputDate):

        # extract day, month and year
        splitInput = inputDate.split('-')
        year = splitInput[0]
        month = splitInput[1]
        day = splitInput[2]

        # add two months and check if month > 12
        month = int(month) + 2
        if month > 12:
            year = str(int(year) + 1)
            # cast to string with leading zeroes on two digits
            month = str(month % 12).zfill(2)
        else:
            month = str(month).zfill(2)

        # rebuild date
        dateToReturn = year + '-' + month + '-' + day

        # Check if the date is valid, otherwise add 60 days
        if self.checkDate(dateToReturn):
            return dateToReturn
        else:
            dateTime = datetime.datetime.strptime(inputDate, '%Y-%m-%d')
            newDate = dateTime + datetime.timedelta(days=60)
            # datetime to string
            newDateStr = newDate.strftime('%Y-%m-%d')
            return newDateStr

    # Simple Check Date for format YYYY-MM-DD, invalids date trigger exeption, too (example: 2019-33-12)
    def checkDate(self, dateStr):
        try:
            datetime.datetime.strptime(dateStr, '%Y-%m-%d')
            return True
        except ValueError:
            return False


    # Save to file function, creates output file name based on input file name
    def saveToFile(self):

        try:
            # create new file name for output by adding current datetime to input file name
            nowDateTime = datetime.datetime.now()
            nowDateTimeStr = nowDateTime.strftime('%Y-%m-%d_%H-%M-%S')

            self.outputFileName = 'DSP_' + self.inputFile.split('.')[0] + '_' + nowDateTimeStr + '.csv'

            # Sort output by DSP (Data Scadenza Pagamento)
            self.sortOutput()

            # write file
            with open(self.outputFileName, 'wb') as myfile:
                wr = csv.writer(myfile, delimiter=self.csvDelimiter)
                # write header, then data
                wr.writerow(self.outputCols)
                for singleRow in self.outputData:
                    wr.writerow(singleRow)

        except Exception as e:
            # handle unexpected script errors
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.errorHandler(e, 'saveToFile()', exc_tb.tb_lineno)

    # This method sorts output by DPS (Data Scadenza Pagamento)
    def sortOutput(self):
        # x[2] represents the dps field, and it's used as a key to sort the two-dimensional array
        self.outputData.sort(key = lambda x: x[2])

