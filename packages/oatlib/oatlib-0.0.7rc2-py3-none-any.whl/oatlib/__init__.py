"""
    Python package `oatlib` provides objects and methods to manipulate 
    obeservation time series.  
    It support data loading, export and saving
    on different format (CSV, sqlite, istSOS).

    Overview
    ---------
    [![](https://img.shields.io/badge/PDF-open_or_download-black)](https://raw.githubusercontent.com/istSOS/workshop/master/oat/oat_tutorial_v4.pdf)

    Code
    -----
    [![](https://img.shields.io/static/v1?logo=gitlab&label=repo&message=on GitLab&color=orange)](https://gitlab.com/ist-supsi/OAT.git)

    Install
    -------
        > pip install oatlib
    
    Quick start
    -----------
    ```python
        from oatlib import sensor, oat_utils

        Q_VED = sensor.Sensor(
            name='CAVERGNO',
            lat=46.34300,
            lon=8.60875,
            alt=455,
            tz= '+02:00',
            prop='air:temperature',
            unit='celsius'
        )
        
        Q_VED.ts_from_csv(
            'https://raw.githubusercontent.com/istSOS/workshop/master/oat/data//Q_VED_ISO_20180101000000000000.dat',
            qualitycol=2,
            sep=',',
            skiprows=1
        )
        
        Q_VED.ts['data'].plot(figsize=(16,5))
        
        print(Q_VED)
    ```
    
    License 
    ------- 
    `oatlib` is licensed under the terms of GNU GPL-2 or later, 
    meaning you can use it for any reasonable purpose and remain in 
    complete ownership of all the documentation you produce, 
    but you are also encouraged to make sure any upgrades to `oatlib` 
    itself find their way back to the community. 
    
    [GPL](https://www.gnu.org/licenses/licenses.html#GPL)
"""

# -*- coding: utf-8 -*-
# ===============================================================================
#
#
# Copyright (c) 2015 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# ===============================================================================
__all__ = ["sensor", "method", "oat_utils", "oat_algorithms"]
__version__ = "0.0.7rc1"

