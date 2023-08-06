# datasnooping.py
#
# Class which computes residuals and removes outliers
#
# This file is part of HectorP 0.0.7.
#
# HectorP is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
#
# HectorP is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# HectorP. If not, see <https://www.gnu.org/licenses/>.
#
# 6/2/2022 Machiel Bos
#===============================================================================

import numpy as np
import sys
import math
from hectorp.observations import Observations
from hectorp.designmatrix import DesignMatrix
from hectorp.control import Control

#==============================================================================
# Subroutines
#==============================================================================

class DataSnooping:

    def __init__(self):
        """ initialise class
        """

        #--- Get control parameters
        control = Control()
        try:
            self.verbose = control.params['Verbose']
        except:
            self.verbose = True

        self.IQ_factor = control.params['IQ_factor']

        #--- Get other classes
        self.obs = Observations()
        self.des = DesignMatrix()

        #--- Copy observations and design matrix into class 
        self.x   = self.obs.data['obs'].to_numpy()
        self.H   = self.des.H

        (m,n) = self.H.shape
        self.m = m 
        self.n = n 

        #--- important variables
        self.res = np.zeros(m)



    def run(self,output):
        """ Mark outliers in the observations as NaN's

        """

        #--- For json file
        output['N'] = self.m  # number of observations

        n_outliers = 1
        outliers = []
        while n_outliers>0:

            #--- matrix F which number of columns = count missing data
            (m,k) = self.obs.F.shape

            #--- leave out rows & colums with gaps 
            xm = np.zeros((m-k))
            Hm = np.zeros((m-k,self.n))
            j = 0
            for i in range(0,m):
                if math.isnan(self.x[i])==False:
                    xm[j] = self.x[i]
                    Hm[j,:] = self.H[i,:]
                    j += 1

            #--- Ordinary Least-Squares
            theta = np.linalg.lstsq(Hm, xm, rcond=None)[0]
            res   = self.x - self.H @ theta  # H has no NaN's

            threshold = self.IQ_factor * (np.nanpercentile(res, 75) - \
						np.nanpercentile(res, 25))
            median   = np.nanpercentile(res, 50)

            n_outliers = 0
            for i in range(0,m):
                if not math.isnan(self.x[i]) and abs(res[i]-median)>threshold:
                    self.x[i] = np.nan
                    n_outliers += 1
                    self.obs.set_NaN(i)
                    outliers.append(self.obs.data.index[i])

            if self.verbose==True: 
                print('Found {0:d} outliers, threshold={1:f}'.format(\
							n_outliers,threshold)) 

        output['outliers'] = outliers 
