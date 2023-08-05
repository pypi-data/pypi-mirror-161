#
#  --------------------------------------------------------------------------
#   mildtrix Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                $Date$
#                $Author$
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
from .MTCommon import MTCommon

###Python 2 requires this
#pylint: disable=bad-option-value,old-style-class
class ReceiveEventArgs:
    """Argument class for IMTMedia data received events."""
    #pylint: disable=too-few-public-methods

    def __init__(self, data=None, senderInfo=None):
        """
        Constructor.

        data : Received data.
        senderInfo : Sender information.
        """
        ###Received data.
        self.data = data
        self.senderInformation = senderInfo

    def __str__(self):
        if isinstance(self.data, (bytearray, bytes)):
            return self.senderInformation + ":" + MTCommon.toHex(self.data)
        return self.senderInformation + ":" + str(self.data)
