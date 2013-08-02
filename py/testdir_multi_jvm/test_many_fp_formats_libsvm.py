import unittest
import random, sys, time, os
sys.path.extend(['.','..','py'])

import h2o, h2o_cmd, h2o_hosts, h2o_browse as h2b, h2o_import as h2i, h2o_exec as h2e

def write_syn_dataset(csvPathname, rowCount, colCount, SEEDPERFILE, sel, distribution):
    # we can do all sorts of methods off the r object
    r = random.Random(SEEDPERFILE)

    def e0(val): return "%e" % val
    def e1(val): return "%20e" % val
    def e2(val): return "%-20e" % val
    def e3(val): return "%020e" % val
    def e4(val): return "%+e" % val
    def e5(val): return "%+20e" % val
    def e6(val): return "%+-20e" % val
    def e7(val): return "%+020e" % val
    def e8(val): return "%.4e" % val
    def e9(val): return "%20.4e" % val
    def e10(val): return "%-20.4e" % val
    def e11(val): return "%020.4e" % val
    def e12(val): return "%+.4e" % val
    def e13(val): return "%+20.4e" % val
    def e14(val): return "%+-20.4e" % val
    def e15(val): return "%+020.4e" % val

    def f0(val): return "%f" % val
    def f1(val): return "%20f" % val
    def f2(val): return "%-20f" % val
    def f3(val): return "%020f" % val
    def f4(val): return "%+f" % val
    def f5(val): return "%+20f" % val
    def f6(val): return "%+-20f" % val
    def f7(val): return "%+020f" % val
    def f8(val): return "%.4f" % val
    def f9(val): return "%20.4f" % val
    def f10(val): return "%-20.4f" % val
    def f11(val): return "%020.4f" % val
    def f12(val): return "%+.4f" % val
    def f13(val): return "%+20.4f" % val
    def f14(val): return "%+-20.4f" % val
    def f15(val): return "%+020.4f" % val

    def g0(val): return "%g" % val
    def g1(val): return "%20g" % val
    def g2(val): return "%-20g" % val
    def g3(val): return "%020g" % val
    def g4(val): return "%+g" % val
    def g5(val): return "%+20g" % val
    def g6(val): return "%+-20g" % val
    def g7(val): return "%+020g" % val
    def g8(val): return "%.4g" % val
    def g9(val): return "%20.4g" % val
    def g10(val): return "%-20.4g" % val
    def g11(val): return "%020.4g" % val
    def g12(val): return "%+.4g" % val
    def g13(val): return "%+20.4g" % val
    def g14(val): return "%+-20.4g" % val
    def g15(val): return "%+020.4g" % val

    # try a neat way to use a dictionary to case select functions
    # didn't want to use python advanced string format with variable as format
    # because they do left/right align outside of that??
    caseList=[
        e0, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11, e12, e13, e14, e15,
        f0, f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15,
        g0, g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12, g13, g14, g15,
        ]

    if sel<0 or sel>=len(caseList):
        raise Exception("sel out of range in write_syn_dataset:", sel)
    f = caseList[sel]

    def makeVal(valMin,valMax):
        ## val = r.uniform(MIN,MAX)
        val = r.triangular(valMin,valMax,0)
        # force it to be zero in this range. so we don't print zeroes for svm!
        if (val > valMin/2) and (val < valMax/2):
            return None
        else:
            return val

    valMin = -1e2
    valMax =  1e2
    classMin = -36
    classMax = 36
    dsf = open(csvPathname, "w+")
    for i in range(rowCount):
        rowData = []
        d = random.randint(0,2)
        if d==0:
            if distribution == 'sparse':
                # only one value per row!
                j = random.randint(0, colCount)
                val = makeVal(valMin, valMax)
                # cols start with 1!
                if val:
                    rowData.append(str(j+1) + ":" + f(val)) # f should always return string
            else:
                # some number of values per row.. 50% or so?
                for j in range(colCount):
                    val = makeVal(valMin, valMax)
                    # cols start with 1!
                    if val:
                        rowData.append(str(j+1) + ":" + f(val)) # f should always return string

            if len(rowData)!=0:
                # space is the only valid separator
                # random integer for class
                rowData.insert(0, random.randint(classMin,classMax))

        rowDataCsv = " ".join(map(str,rowData))
        # FIX! vary the eol ?
        # randomly skip some rows. only write 1/3
        dsf.write(rowDataCsv + "\n")

    dsf.close()

class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        global SEED, localhost
        SEED = h2o.setup_random_seed()
        localhost = h2o.decide_if_localhost()
        if (localhost):
            h2o.build_cloud(2,java_heap_GB=5)
        else:
            h2o_hosts.build_cloud_with_hosts()

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_many_cols_and_values_with_syn(self):
        SYNDATASETS_DIR = h2o.make_syn_dir()
        tryList = [
            (1000, 10, 'cA', 30, 'sparse'),
            (100000, 1000, 'cA', 30, 'sparse'),
            (1000, 10, 'cA', 30, 'sparse50'),
            (100, 1000, 'cB', 30,'sparse'),
            (100, 1000, 'cB', 30,'sparse50'),
            # (100, 900, 'cC', 30),
            # (100, 500, 'cD', 30),
            # (100, 100, 'cE', 30),
            ]

        # h2b.browseTheCloud()
        for (rowCount, colCount, key2, timeoutSecs, distribution) in tryList:
            for sel in range(48): # len(caseList)
                SEEDPERFILE = random.randint(0, sys.maxint)
                csvFilename = "syn_%s_%s_%s_%s.csv" % (SEEDPERFILE, sel, rowCount, colCount)
                csvPathname = SYNDATASETS_DIR + '/' + csvFilename

                print "Creating random", csvPathname
                write_syn_dataset(csvPathname, rowCount, colCount, SEEDPERFILE, sel, distribution)

                selKey2 = key2 + "_" + str(sel)
                parseKey = h2o_cmd.parseFile(None, csvPathname, key2=selKey2, timeoutSecs=timeoutSecs)
                print csvFilename, 'parse time:', parseKey['response']['time']
                print "Parse result['destination_key']:", parseKey['destination_key']
                inspect = h2o_cmd.runInspect(None, parseKey['destination_key'])
                print "\n" + csvFilename

                # if not h2o.browse_disable:
                #     h2b.browseJsonHistoryAsUrlLastMatch("Inspect")
                #     time.sleep(3)

if __name__ == '__main__':
    h2o.unit_main()
