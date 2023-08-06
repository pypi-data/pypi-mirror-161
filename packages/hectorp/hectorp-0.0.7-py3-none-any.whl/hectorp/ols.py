# ols.py
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
# 19/5/2020  David Bugalho & Machiel Bos
#===============================================================================

import numpy as np
import math
from numpy.linalg import inv

#===============================================================================
# Class definitions
#===============================================================================

class OLS:

    def compute_leastsquares(self,t,H,x,F,samenoise=False):
        """ Compute ordinary least-squares 
 
        Args:
            t (m*1 matrix) : first column of Toeplitz covariance matrix C
            H (m*n matrix) : design matrix
            x (m*1 matrix) : observations
            F (m*k matrix) : special matrix to deal with missing data [not used]
            samenoise (bool): use old covariance matrix or not

   
        Returns:
            theta (n*1 matrix)    : estimated parameters
            C_theta  (n*n matrix) : covariance matrix of estimated parameters
            ln_det_C (float)      : log(det(C))
            sigma_eta (float)     : driving noise
        """

        #--- Get size of matrix H
        (m,n) = H.shape

        #--- Get size of matrix F which number of columns = count missing data
        (m,k) = F.shape

        #--- leave out rows & colums with gaps
        xm = np.zeros((m-k))
        Hm = np.zeros((m-k,n))
        ii = 0
        for i in range(0,m):
            if math.isnan(x[i])==False:
                xm[ii] = x[i]
                Hm[ii,:] = H[i,:]
                ii += 1

        #--- Compute logarithm of determinant of C
        ln_det_C = 0.0

        #--- Compute C_theta
        C_theta = inv(Hm.T @ Hm)
        theta = C_theta @ (Hm.T @ xm)

        #--- Compute model, whitened residuals and sigma_eta
        xhat = Hm @ theta
        r = xm - xhat
        sigma_eta = math.sqrt(np.dot(r,r)/(m-k))

        return [theta,C_theta,ln_det_C,sigma_eta]
