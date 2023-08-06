# -*- coding: utf-8 -*-
#
# This small program computes the Modified Julian Date (MJD).
#
#  This script is part of HectorP 0.0.7
#
#  HectorP is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  HectorP is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with HectorP. If not, see <http://www.gnu.org/licenses/>
#
# 14/2/2022 Machiel Bos, Santa Clara
#===============================================================================

import sys
from hectorp.calendar import compute_mjd

#===============================================================================
# Main program
#===============================================================================

def main():

    args = sys.argv[1:]

    if len(args)!=6:
        print("Correct input: date2MJD year month day hour minute second")
        sys.exit()
    else:
        year  = int(args[0])
        month = int(args[1])
        day   = int(args[2])
        hour  = int(args[3])
        minute= int(args[4])
        second= float(args[5])
        mjd = compute_mjd(year,month,day,hour,minute,second)
        print("year   : {0:4d}".format(year))
        print("month  : {0:4d}".format(month))
        print("day    : {0:4d}".format(day))
        print("hour   : {0:4d}".format(hour))
        print("minute : {0:4d}".format(minute))
        print("second : {0:f}".format(second))
        print("MJD    : {0:f}".format(mjd))
