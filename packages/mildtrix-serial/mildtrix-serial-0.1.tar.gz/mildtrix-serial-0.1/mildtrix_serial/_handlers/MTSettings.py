#
#  --------------------------------------------------------------------------
#   mildtrix Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) mildtrix Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of mildtrix Device Framework.
#
#  mildtrix Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  mildtrix Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of mildtrix products: http://www.mildtrix.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
import mildtrix_common.io.BaudRate
import mildtrix_common.io.Parity
import mildtrix_common.io.StopBits

###Python 2 requires this
# pylint: disable=bad-option-value,old-style-class,too-few-public-methods
class MTSettings:

    def __init__(self,
                 baudRate=mildtrix_common.io.BaudRate.BAUD_RATE_9600,
                 dataBits=8,
                 parity=mildtrix_common.io.Parity.NONE,
                 stopBits=mildtrix_common.io.StopBits.ONE):
        self.baudrate = baudRate
        self.dataBits = dataBits
        self.parity = parity
        self.stopBits = stopBits
