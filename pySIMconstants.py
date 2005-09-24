# Copyright (C) 2005, Todd Whiteman
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

#===============================================================================
#                          C O N S T A N T S
#===============================================================================

SCARD_PROTOCOL_T0   = 1
SCARD_PROTOCOL_T1   = 2

SIM_STATE_DISCONNECTED  = 0
SIM_STATE_CONNECTED     = 1

SW_OK                   = "9000"
SW_FOLDER_SELECTED_OK   = "9F17"
SW_FILE_SELECTED_OK     = "9F0F"

CHV_ALWAYS              = 0
CHV_READ                = 1
CHV_UPDATE              = 2

ATTRIBUTE_ATR               = 0x90303
ATTRIBUTE_VENDOR_NAME       = 0x10100
ATTRIBUTE_VENDOR_SERIAL_NO  = 0x10103
