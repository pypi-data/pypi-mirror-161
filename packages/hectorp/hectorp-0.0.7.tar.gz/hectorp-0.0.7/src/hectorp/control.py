# control.py
#
# This file is part of HectorP 0.0.7
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
# 29/12/2021  Machiel Bos, Santa Clara
#==============================================================================

import os
import sys

#==============================================================================
# Class definition
#==============================================================================

class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]



    def clear(cls):
        _ = cls._instances.pop(cls, None)



    def clear_all(*args, **kwargs):
        SingletonMeta._instances = {}



class Control(metaclass=SingletonMeta):
    """Class to store parameters that prescribe how the analysis should be done
    """
   
    def __init__(self, ctl_file):
        """This is my Control class

        Args:
            ctl_file (string) : name of text-file with parameters
        """

        self.params = {}
   
        file_exists = os.path.exists(ctl_file) 
        if file_exists==False:
            print('Cannot open {0:s}'.format(ctl_file))
            sys.exit()
        else:
            with open(ctl_file,'r') as fp:
                for line in fp:
                    cols = line.split()
                    label = cols[0]
                    if cols[1]=='Yes' or cols[1]=='yes':
                        self.params[label] = True
                    elif cols[1]=='No' or cols[1]=='no':
                        self.params[label] = False
                    elif cols[1].isdigit()==True:
                        self.params[label] = int(cols[1])
                    else:
                        if self.is_float(cols[1])==True:
                            if len(cols)==2:
                                self.params[label] = float(cols[1])
                            else:
                                self.params[label] = []
                                for i in range(1,len(cols)):
                                   self.params[label].append(float(cols[i]))
                        else:
                            if len(cols)==2:
                                self.params[label] = cols[1]
                            elif len(cols)>2:
                                self.params[label] = cols[1:]
                            else:
                                print('found label {0:s} but no value!'.\
								format(label))
                                sys.exit()


    def is_float(self,x):
        """ Check if string is float

        Args:
           x (string) : is this a float string?

        Returns:
           True is number is float
        """
        try:
            float(x)
            return True
        except ValueError:
            return False
