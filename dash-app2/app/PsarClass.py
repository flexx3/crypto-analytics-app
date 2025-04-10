from collections import deque

class PSAR:
    def __init__(self, init_af=0.02, max_af=0.2, af_step=0.02):
        self.init_af= init_af
        self.af= init_af
        self.max_af= max_af
        self.af_step= af_step
        self.extreme_point= None
        self.high_price_trend= []
        self.low_price_trend= []
        self.high_price_window= deque(maxlen=2)
        self.low_price_window= deque(maxlen=2)
        
        #list to track result
        self.psarList= []
        self.afList= []
        self.epList= []
        self.highList= []
        self.lowList= []
        self.trendList= []
        self.nDays= 0
        
    def calcPSAR(self, high, low):
        #ensure 2-day window
        if self.nDays>= 3:
            psar= self._calcPSAR()
            
        else:
            psar= self._initPSARVals(high,low)
            
        psar= self._UpdateCurrentVals(psar, high, low)
        self.nDays+= 1
        return psar
    
    def _initPSARVals(self, high, low):
        if len(self.low_price_window)<=1:
            self.trend= None
            self.extreme_point= high
            return None
        #calculate trend get initial psar, extremepoint based on trend
        if self.high_price_window[0]<self.high_price_window[1]:
            self.trend= 1
            psar= min(self.low_price_window)
            self.extreme_point= max(self.high_price_window)
        else:
            self.trend= 0
            self.extreme_point= min(self.high_price_window)
            psar= max(self.low_price_window)
        return psar
    
    def _calcPSAR(self):
        prev_psar= self.psarList[-1]
        if self.trend == 1:
            psar= prev_psar + self.af*(self.extreme_point - prev_psar)
            psar= min(psar, min(self.low_price_window))
            
        else:
            psar= prev_psar - self.af*(prev_psar - self.extreme_point)
            psar= max(psar, max(self.high_price_window))
        return psar
    
    def _UpdateCurrentVals(self, psar, high, low):
        if self.trend == 1:
            self.high_price_trend.append(high)
        elif self.trend == 0:
            self.low_price_trend.append(low)
        
        psar = self._trendReversal(psar, high, low)
        self.psarList.append(psar)
        self.afList.append(self.af)
        self.epList.append(self.extreme_point)
        self.highList.append(high)
        self.lowList.append(low)
        self.high_price_window.append(high)
        self.low_price_window.append(low)
        self.trendList.append(self.trend)
        return psar
    def _trendReversal(self, psar, high, low):
        # Checks for reversals
        reversal = False
        if self.trend == 1 and psar > low:
            self.trend = 0
            psar = max(self.high_price_trend)
            self.extreme_point = low
            reversal = True
        elif self.trend == 0 and psar < high:
            self.trend = 1
            psar = min(self.low_price_trend)
            self.extreme_point = high
            reversal = True

        if reversal:
            self.af = self.init_af
            self.high_price_trend.clear()
            self.low_price_trend.clear()
        else:
            if high > self.extreme_point and self.trend == 1:
                self.af = min(self.af + self.af_step, self.max_af)
                self.extreme_point = high
            elif low < self.extreme_point and self.trend == 0:
                self.af = min(self.af + self.af_step, self.max_af)
                self.extreme_point = low

        return psar

