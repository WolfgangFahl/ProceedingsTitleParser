'''
Created on 2020-07-05

@author: wf
'''
import unittest


from ptp.plot import Plot

class TestPlot(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testPlot(self):
        ''' test a plot based on a Counter '''
        valueList=['A','B','A','C','A','A'];
        plot=Plot(valueList,"barchart example",xlabel="Char",ylabel="frequency")
        plot.barchart(mode='save')
        plot.title="histogram example"
        plot.debug=True
        plot.hist(mode='save')        
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()