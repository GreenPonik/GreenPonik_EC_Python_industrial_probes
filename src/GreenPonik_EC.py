"""
####################################################################
####################################################################
####################################################################
################ GreenPonik Read EC through Python3 ################
################ Use only with industrial probes 1/2 ###############
####################################################################
####################################################################
####################################################################
Based on GreenPonik_EC_Python library
https://github.com/GreenPonik/GreenPonik_EC_Python

Need DFRobot_ADS1115 library
https://github.com/DFRobot/DFRobot_ADS1115/tree/master/RaspberryPi/Python
"""
import time

_kvalue = 1.0
_kvalueLow = 1.0
_kvalueHigh = 1.0
_voltage = 0.0
_temperature = 25.0

_raw_1413 = 1.200
_raw_1413_offset = 0.750
_raw_276 = 2.500
_raw_276_offset_low = 0.500
_raw_276_offset_high = 1.000
_raw_1288 = 11.850
_raw_1288_offset = 3.650

TXT_FILE_PATH = "/home/greenponik/bundle_project_raspberry_core/"


class GreenPonik_EC():
    def begin(self):
        global _kvalueLow
        global _kvalueHigh
        try:
            print(">>>Initialization of ec lib<<<")
            with open('%secdata.txt' % TXT_FILE_PATH, 'r') as f:
                kvalueLowLine = f.readline()
                kvalueLowLine = kvalueLowLine.strip('kvalueLow=')
                _kvalueLow = float(kvalueLowLine)
                print("get k value low from txt file: %.3f" % _kvalueLow)
                kvalueHighLine = f.readline()
                kvalueHighLine = kvalueHighLine.strip('kvalueHigh=')
                _kvalueHigh = float(kvalueHighLine)
                print("get k value high from txt file: %.3f" % _kvalueHigh)
        except:
            self.reset()


    def readEC(self, voltage, temperature):
        global _kvalueLow
        global _kvalueHigh
        global _kvalue
        print(">>>current voltage is: %.3f mV" % voltage)
        rawEC = 1000*voltage/820.0/200.0
        print(">>>current rawEC is: %.3f" % rawEC)
        print(">>>interpolation of k")
        # a = (Y2-Y1)/(X2-X1)
        slope = (_kvalueHigh-_kvalueLow) / (2.76-1.413)
        print(">>>slope: %.5f" % slope)
        # b = Y1 - (a*X1)
        intercept = _kvalueLow - (slope*1.413)
        print(">>>intercept: %.5f" % intercept)
        # y = ax+b
        _kvalue = (slope*rawEC)+intercept
        print(">>>interpolated _kvalue: %.5f" % _kvalue)
        value = rawEC * _kvalue
        value = value / (1.0+0.0185*(temperature-25.0))
        return value

    def KvalueTempCalculation(self, compECsolution, voltage):
        return 820.0*200.0*compECsolution/1000.0/voltage

    def calibration(self, voltage, temperature):
        rawEC = 1000*voltage/820.0/200.0
        print(">>>current rawEC is: %.3f" % rawEC)
        # automated 1.413 buffer solution dection
        if (rawEC > _raw_1413-_raw_1413_offset and rawEC < _raw_1413+_raw_1413_offset):
            compECsolution = 1.413*(1.0+0.0185*(temperature-25.0))
            KValueTemp = self.KvalueTempCalculation(compECsolution, voltage)
            KValueTemp = round(KValueTemp, 2)
            print(">>>Buffer Solution:1.413us/cm")
            f = open('%secdata.txt' % TXT_FILE_PATH, 'r+')
            flist = f.readlines()
            flist[0] = 'kvalueLow=' + str(KValueTemp) + '\n'
            f = open('%secdata.txt' % TXT_FILE_PATH, 'w+')
            f.writelines(flist)
            f.close()
            status_msg = ">>>EC:1.413us/cm Calibration completed<<<"
            print(status_msg)
            time.sleep(5.0)
            cal_res = {'status': 1413,
                       'kvalue': KValueTemp,
                       'status_message': status_msg}
            return cal_res
        # automated 2.76 buffer solution dection
        elif (rawEC > _raw_276-_raw_276_offset_low and rawEC < _raw_276+_raw_276_offset_high):
            compECsolution = 2.76*(1.0+0.0185*(temperature-25.0))
            KValueTemp = self.KvalueTempCalculation(compECsolution, voltage)
            KValueTemp = round(KValueTemp, 2)
            print(">>>Buffer Solution:2.76ms/cm")
            f = open('%secdata.txt' % TXT_FILE_PATH, 'r+')
            flist = f.readlines()
            flist[1] = 'kvalueHigh=' + str(KValueTemp) + '\n'
            f = open('%secdata.txt' % TXT_FILE_PATH, 'w+')
            f.writelines(flist)
            f.close()
            status_msg = ">>>EC:2.76ms/cm Calibration completed<<<"
            print(status_msg)
            time.sleep(5.0)
            cal_res = {'status': 276,
                       'kvalue': KValueTemp,
                       'status_message': status_msg}
            return cal_res
        # automated 12.88 buffer solution dection
        # elif (rawEC > _raw_1288-_raw_1288_offset and rawEC < _raw_1288+_raw_1288_offset):
        #     compECsolution = 12.88*(1.0+0.0185*(temperature-25.0))
        #     KValueTemp = self.KvalueTempCalculation(compECsolution, voltage)
        #     print(">>>Buffer Solution:12.88ms/cm")
        #     f = open('%secdata.txt' % TXT_FILE_PATH, 'r+')
        #     flist = f.readlines()
        #     flist[1] = 'kvalueHigh=' + str(KValueTemp) + '\n'
        #     f = open('%secdata.txt' % TXT_FILE_PATH, 'w+')
        #     f.writelines(flist)
        #     f.close()
        #     status_msg = ">>>EC:12.88ms/cm Calibration completed<<<"
        #     print(status_msg)
        #     time.sleep(5.0)
        #     cal_res = {'status': 1288,
        #                'kvalue': KValueTemp,
        #                'status_message': status_msg}
        #     return cal_res
        else:
            status_msg = ">>>Buffer Solution Error, EC raw: %.3f, Try Again<<<" % rawEC
            print(status_msg)
            cal_res = {'status': 9999, 'status_message': status_msg}
            return cal_res

    def reset(self):
        global _kvalueLow
        global _kvalueHigh
        _kvalueLow = 1.0
        _kvalueHigh = 1.0
        print(">>>Reset to default parameters<<<")
        try:
            print(">>>Read k from txt files<<<")
            f = open('%secdata.txt' % TXT_FILE_PATH, 'r+')
            flist = f.readlines()
            flist[0] = 'kvalueLow=' + str(_kvalueLow) + '\n'
            flist[1] = 'kvalueHigh=' + str(_kvalueHigh) + '\n'
            f = open('%secdata.txt' % TXT_FILE_PATH, 'w+')
            f.writelines(flist)
            f.close()
        except:
            print(">>>Cannot read k from txt files<<<")
            print(">>>Let's create them and apply the default values<<<")
            f = open('%secdata.txt' % TXT_FILE_PATH, 'w')
            flist = 'kvalueLow=' + str(_kvalueLow) + '\n'
            flist += 'kvalueHigh=' + str(_kvalueHigh) + '\n'
            f.writelines(flist)
            f.close()
