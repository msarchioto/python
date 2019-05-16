import unittest
import fatturazione

class TestFatturazione(unittest.TestCase):

    # This method tests the date check
    def testCheckDate(self):
        inputDate1 = '2019-05-06'
        inputDate2 = '2019-14-06'
        inputDate3 = '2019-01-32'

        # declare class instance - input files and logger not required for this test
        fattWorker = fatturazione.Fatturazione(None, None, None)

        result1 = fattWorker.checkDate(inputDate1)
        result2 = fattWorker.checkDate(inputDate2)
        result3 = fattWorker.checkDate(inputDate3)

        self.assertEqual(result1, True, 'Date should be valid')
        self.assertEqual(result2, False, 'Date should be invalid')
        self.assertEqual(result3, False, 'Date should be invalid')


    # This method tests the DM Date conversion
    def testDM(self):

        # the df methods expects a dict input
        inputLine1 = {'NrFattura': 'Mock-Fattura-1', 'DataFattura': '2019-05-06', 'ModalitaDiPagamento': 'DF'}
        inputLine2 = {'NrFattura': 'Mock-Fattura-2', 'DataFattura': '2019-02-06', 'ModalitaDiPagamento': 'DF'}
        inputLine3 = {'NrFattura': 'Mock-Fattura-3', 'DataFattura': '2019-12-06', 'ModalitaDiPagamento': 'DF'}

        # declare class instance - input files and logger not required for this test
        fattWorker = fatturazione.Fatturazione(None, None, None)

        fattWorker.dfHandler(inputLine1)
        fattWorker.dfHandler(inputLine2)
        fattWorker.dfHandler(inputLine3)

        # extract from output
        result1 = fattWorker.outputData[0]
        result2 = fattWorker.outputData[1]
        result3 = fattWorker.outputData[2]

        # DataScadenzaPagamento is at the index=2 in the result array
        self.assertEqual(result1[2], inputLine1['DataFattura'], 'Date Should Be Equal')
        self.assertEqual(result2[2], inputLine2['DataFattura'], 'Date Should Be Equal')
        self.assertEqual(result3[2], inputLine3['DataFattura'], 'Date Should Be Equal')


    # This method tests the DMMF Date conversion (end of month)
    def testDMMF(self):

        # the df method expects a dict input
        inputLine1 = {'NrFattura': 'Mock-Fattura-1', 'DataFattura': '2019-05-06', 'ModalitaDiPagamento': 'DMMF'}
        inputLine2 = {'NrFattura': 'Mock-Fattura-2', 'DataFattura': '2019-02-06', 'ModalitaDiPagamento': 'DMMF'}
        inputLine3 = {'NrFattura': 'Mock-Fattura-3', 'DataFattura': '2019-04-06', 'ModalitaDiPagamento': 'DMMF'}

        expectedResult1 = '2019-05-31'
        expectedResult2 = '2019-02-28'
        expectedResult3 = '2019-04-30'

        # declare class instance - input files and logger not required for this test
        fattWorker = fatturazione.Fatturazione(None, None, None)

        fattWorker.dffmHandler(inputLine1)
        fattWorker.dffmHandler(inputLine2)
        fattWorker.dffmHandler(inputLine3)

        # extract from output
        result1 = fattWorker.outputData[0]
        result2 = fattWorker.outputData[1]
        result3 = fattWorker.outputData[2]

        # DataScadenzaPagamento is at the index=2 in the result array
        self.assertEqual(result1[2], expectedResult1, 'Date Should Be Equal')
        self.assertEqual(result2[2], expectedResult2, 'Date Should Be Equal')
        self.assertEqual(result3[2], expectedResult3, 'Date Should Be Equal')


    # This method tests the DM60 Date conversion (+2 months)
    def testDM60(self):

        # the df method expects a dict input
        inputLine1 = {'NrFattura': 'Mock-Fattura-1', 'DataFattura': '2019-05-06', 'ModalitaDiPagamento': 'DM60'}
        inputLine2 = {'NrFattura': 'Mock-Fattura-2', 'DataFattura': '2019-02-01', 'ModalitaDiPagamento': 'DM60'}
        inputLine3 = {'NrFattura': 'Mock-Fattura-3', 'DataFattura': '2018-12-30', 'ModalitaDiPagamento': 'DM60'}

        expectedResult1 = '2019-07-06'
        expectedResult2 = '2019-04-01'
        # for this example it should just add 60 days
        expectedResult3 = '2019-02-28'

        # declare class instance - input files and logger not required for this test
        fattWorker = fatturazione.Fatturazione(None, None, None)

        fattWorker.df60Handler(inputLine1)
        fattWorker.df60Handler(inputLine2)
        fattWorker.df60Handler(inputLine3)

        # extract from output
        result1 = fattWorker.outputData[0]
        result2 = fattWorker.outputData[1]
        result3 = fattWorker.outputData[2]

        # DataScadenzaPagamento is at the index=2 in the result array
        self.assertEqual(result1[2], expectedResult1, 'Date Should Be Equal')
        self.assertEqual(result2[2], expectedResult2, 'Date Should Be Equal')
        self.assertEqual(result3[2], expectedResult3, 'Date Should Be Equal')


    # This method tests the correct sorting of the output
    def testSortOutput(self):

        # declare class instance - input files and logger not required for this test
        fattWorker = fatturazione.Fatturazione(None, None, None)

        # create Mock Output
        mockOutput = [
                        ['Mock-Fattura-1', '0000-00-01', '2019-05-15'],
                        ['Mock-Fattura-2', '0000-00-02', '2019-04-15'],
                        ['Mock-Fattura-3', '0000-00-03', '2019-05-03']
        ]

        # expected result
        sortedOutputManual = [
                        ['Mock-Fattura-2', '0000-00-02', '2019-04-15'],
                        ['Mock-Fattura-3', '0000-00-03', '2019-05-03'],
                        ['Mock-Fattura-1', '0000-00-01', '2019-05-15']
        ]

        # write the mock data into the output
        fattWorker.outputData = mockOutput

        # start sorting
        fattWorker.sortOutput()
        result = fattWorker.outputData

        self.assertItemsEqual(result, sortedOutputManual, 'Arrays Should Be Equal')



if __name__ == '__main__':
    unittest.main()