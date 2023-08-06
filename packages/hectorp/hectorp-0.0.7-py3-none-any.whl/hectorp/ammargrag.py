# ammargrag.py
#
# Python3 implemenation of AmmarGrag.cpp. It provides a quick subroutine to
# perform least-squares given the design matrix H, the observations y and
# the first column of the Toeplitz covariance matrix C.
#
# The Durbin-Levinson algorithm is based on Chapter 3 of "Iterative Methods 
# for Toeplitz Systems", By Michael K. Ng  (page 28-29)
#
# Equations are taken from Bos et al. (2013), "Fast error analysis of 
# continuous GNSS observations with missing data", Journal of Geodesy,
# DOI 10.1007/s00190-012-0605-0.
#
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
# 17/5/2020  Machiel Bos, Santa Clara
#  2/1/2022  Machiel Bos, Santa Clara
#===============================================================================

import numpy as np
import math
import time
from numpy import fft
from numpy.linalg import inv
import datetime
from hectorp.control import SingletonMeta

#===============================================================================
# Class definitions
#===============================================================================

class AmmarGrag(metaclass=SingletonMeta):

    def __init(self):
        """ Define class variables
        """
        self.z
        self.G1
        self.G2
        self.y1
        self.y2
        self.Fl1
        self.Fl2
        self.Minv
        self.Qy
        self.ln_det_C


    def compute_leastsquares(self,t,H,x,F,samenoise=False):
        """ Compute least-squares 
 
        Arg:
            t (m*1 matrix)  : first column of Toeplitz covariance matrix C
            H (m*n matrix)  : design matrix
            x (m*1 matrix)  : observations
            samenoise (bool): use old covariance matrix or not
   
        Returns:
            theta (n*1 matrix)    : estimated parameters
            C_theta  (n*n matrix) : covariance matrix of estimated parameters
            ln_det_C (float)      : log(det(C))
            sigma_eta (float)     : driving noise
        """

        if samenoise==False:
            #--- Get size of matrix H
            (m,n) = H.shape

            #--- Get size of matrix F which number of columns=count missing data
            (m,k) = F.shape

            #--- Durbin-Levinson to compute l1 and l2
            r = np.zeros(m-1)
            delta = t[0]
            self.ln_det_C = math.log(delta)
            for i in range(0,m-1):
                if i==0:
                    gamma = -t[i+1]/delta
                else:
                    gamma = -(t[i+1] + np.dot(t[1:i+1],r[0:i]))/delta
                    r[1:i+1] = r[0:i] + gamma*r[i-1::-1]

                r[0] = gamma
                delta = t[0] + np.dot(t[1:i+2],r[i::-1])
                self.ln_det_C += math.log(delta)
    
            #--- create l1 & l2 using r
            l1 = np.zeros(2*m)
            l2 = np.zeros(2*m)

            l1[0]   = 1.0
            l1[1:m] = r[m-2::-1]
            l2[1:m] = r[0:m-1]

            #-- Scale l1 & l2
            l1 *= 1.0/math.sqrt(delta)
            l2 *= 1.0/math.sqrt(delta)

            #--- Perform FFT on l1 and l2
            self.Fl1 = np.fft.rfft(l1)
            self.Fl2 = np.fft.rfft(l2) 

            #--- Currently there might be NaN's in H and x. Make those zero
            xm = np.zeros(m)
            for i in range(0,m):
                if math.isnan(x[i])==True:
                    xm[i]   = 0.0
                else:
                    xm[i]   = x[i]

            #--- Create auxiliary matrices and vectors
            self.z  = np.zeros(m)
            Fx      = np.fft.rfft(np.concatenate((xm,self.z)))
            self.y1 = (np.fft.irfft(self.Fl1 * Fx, n=2*m))[0:m]
            self.y2 = (np.fft.irfft(self.Fl2 * Fx, n=2*m))[0:m]
        
            #--- Only when there are missing data
            if k>0:
                #--- matrix F
                self.G1 = np.zeros((k,m))
                self.G2 = np.zeros((k,m))
                for i in range(0,k):
                    FF = np.fft.rfft(np.concatenate((F[:,i].T,self.z)))
                    self.G1[i,:] = (np.fft.irfft(self.Fl1 * FF, n=2*m))[0:m]
                    self.G2[i,:] = (np.fft.irfft(self.Fl2 * FF, n=2*m))[0:m]

                #--- Compute matrix M
                M = np.linalg.cholesky(self.G1 @ self.G1.T-self.G2 @ self.G2.T)

                #--- Update ln_det_C
                for i in range(0,k):
                    self.ln_det_C += 2.0*math.log(M[i,i])

                #--- Compute QA and Qy
                self.Minv = inv(M)
                self.Qy = self.Minv @ (self.G1 @ self.y1.T-self.G2 @ self.y2.T)

        #=== END OF THINGS WITHOUT DESIGN MATRIX

        #--- Get size of matrix H (again...)
        (m,n) = H.shape
        (m,k) = F.shape
        A1 = np.zeros((n,m))
        A2 = np.zeros((n,m))

        Hm = np.zeros((m,n))
        for i in range(0,m):
            if math.isnan(x[i])==True:
                Hm[i,:] = 0.0
            else:
                Hm[i,:] = H[i,:]

        for i in range(0,n):
            FH = np.fft.rfft(np.concatenate((Hm[:,i].T,self.z)))
            A1[i,:] = (np.fft.irfft(self.Fl1 * FH, n=2*m))[0:m]
            A2[i,:] = (np.fft.irfft(self.Fl2 * FH, n=2*m))[0:m]

        if k>0:
            QA = self.Minv @ (self.G1 @ A1.T - self.G2 @ A2.T)

            #--- Least-squares
            C_theta = inv(A1 @ A1.T - A2 @ A2.T - QA.T @ QA)
            theta = C_theta @ (A1 @ self.y1.T - A2 @ self.y2.T - QA.T @ self.Qy)

            #--- Compute sigma_eta
            t1 = self.y1 - A1.T @ theta
            t2 = self.y2 - A2.T @ theta

            #--- Compute Qt
            Qt = self.Minv @ (self.G1 @ t1.T - self.G2 @ t2.T)

            sigma_eta = math.sqrt((np.dot(t1,t1) - np.dot(t2,t2) \
						      - np.dot(Qt,Qt))/(m-k))
        else:
            #--- Least-squares with no missing data
            C_theta = inv(A1 @ A1.T - A2 @ A2.T)
            theta = C_theta @ (A1 @ self.y1.T - A2 @ self.y2.T) 

            #--- Compute sigma_eta
            t1 = self.y1 - A1.T @ theta
            t2 = self.y2 - A2.T @ theta
            sigma_eta = math.sqrt((np.dot(t1,t1) - np.dot(t2,t2))/m)

        return [theta,C_theta,self.ln_det_C,sigma_eta]
