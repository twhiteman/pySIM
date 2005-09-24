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

"""
'pySIMutil.py'
Contains some utilities functions:
    - swapNibbles(hexString, paddingNibble='F'):
          converts a string in a buffer with swap of each character
          sample : "0139664372" is converted in [0X10, 0X93, 0X66, 0X34, 0X27 ]
    - APDUPadd(apdu, length, padding='F'):
          padd an APDU.
    - ASCIIToList(sName):
          converts a name string in a byte list
          sample : "Pascal" is converted in
          [0X50,0X61,0X73,0X63,0X61,0X6C]
    - ASCIIToGSM3_38(sName):
          converts a name string in a byte list using GSM 3.38 conversion table
    - ASCIIToPIN( sPIN ):
          converts a PIN code string in a buffer with padd
          sample : "0000" is converted in [0X30, 0X30, 0X30, 0X30, 0XFF, 0XFF, 0XFF, 0XFF ]

"""

#===============================================================================
#                          F U N C T I O N S
#===============================================================================

def swapNibbles(hexString, paddingNibble='F'):
    """ converts a string in a buffer with swap of each character
        If odd number of characters, the paddingNibble is concatened to the result string
        before swap.
        sample : "01396643721" is converted to "1093663427F1"
        Input :
            - hexString     = string containing data to swap
            - paddingNibble = value of the padd (optional parameter, default value is 'F')
        
        Return a list of bytes.
    """
    remove_pad = 0
    length = len(hexString)
    if length >= 2 and hexString[-2] == paddingNibble:
        remove_pad = 1

    if (length % 2):       # need padding
        hexString += paddingNibble

    res = ''
    for i in range(0, length, 2):
        res += "%s%s" % (hexString[i+1], hexString[i])

    if remove_pad:
        res = res[:-1]
    return res

#===============================================================================

def StringToGSMPhoneNumber(phoneString):
    """ converts a number string to a GSM number string representation
        Input :
            - phoneString    = phone string (data to swap)
        Returns a GSM number string.
    """
    if not phoneString:
        return ''

    if phoneString[0] == '+':
        res = "91"
        phoneString = phoneString[1:]
    else:
        res = "81"

    if len(phoneString) % 2:
        phoneString += "F"

    i = 0
    while i < len(phoneString):
        res += '%s%s' % (phoneString[i+1], phoneString[i])
        i += 2

    return res

#===============================================================================

def GSMPhoneNumberToString(phoneString, replaceTonNPI=0):
    """ converts a GSM string number to a normal string representation
        If the second last character is 'F', the F is removed from the result string.
        sample : "10936634F7"  is converted to "013966437"
        Input :
            - phoneString    = GSM phone string (data to swap)
        Returns a normal number string.
    """
    if not phoneString:
        return ''

    res = ""
    if replaceTonNPI:
        if phoneString[:2] == "91":
            res = "+"
        phoneString = phoneString[2:]

    i = 0
    while i < len(phoneString):
        res += '%s%s' % (phoneString[i+1], phoneString[i])
        i += 2

    if res and res[-1].upper() == 'F':
        res = res[:-1]

    return res

#===============================================================================

# GSM3.38 character conversion table
dic_GSM_3_38 = { '@':0x00,                                # @ At symbol
                 chr(0x9C):0x01,                          # £ Britain pound symbol
                 '$':0x02,                                # $ Dollar symbol
                 chr(0xA5):0x03,                          # ¥ Yen symbol
                 'è':0x04,                                # è e accent grave
                 'é':0x05,                                # é e accent aigu
                 'ù':0x06,                                # ù u accent grave
                 chr(0xEC):0x07,                          # ì i accent grave
                 chr(0xF2):0x08,                          # ò o accent grave
                 chr(0xC7):0x09,                          # Ç C majuscule cedille
                 chr(0x0A):0x0A,                          # LF Line Feed
                 chr(0xD8):0x0B,                          # Ø O majuscule barré
                 chr(0xF8):0x0C,                          # ø o minuscule barré
                 chr(0x0D):0x0D,                          # CR Carriage Return
                 chr(0xC5):0x0E,                          # Å Angstroem majuscule
                 chr(0xE5):0x0F,                          # å Angstroem minuscule

                 '_':0x11,                                # underscore
                 chr(0xC6):0x1C,                          # Æ majuscule ae
                 chr(0xE6):0x1D,                          # æ minuscule ae
                 chr(0xDF):0x1E,                          # ß s dur allemand
                 chr(0xC9):0x1F,                          # É majuscule é

                 ' ':0x20, '!':0x21,
                 '\"':0x22,                               # guillemet
                 '#':0x23,
                 '¤':0x24,                                # ¤ carré

                 chr(0xA1):0x40,                          # ¡ point d'exclamation renversé

                 chr(0xC4):0x5B,                          # Ä majuscule A trema
                 chr(0xE4):0x7B,                          # ä minuscule a trema

                 chr(0xD6):0x5C,                          # Ö majuscule O trema
                 chr(0xF6):0x7C,                          # ö minuscule o trema

                 chr(0xD1):0x5D,                          # Ñ majuscule N tilda espagnol
                 chr(0xF1):0x7D,                          # ñ minuscule n tilda espagnol

                 chr(0xDC):0x5E,                          # Ü majuscule U trema
                 chr(0xFC):0x7E,                          # ü minuscule u trema

                 chr(0xA7):0x5F,                          # § signe paragraphe

                 chr(0xBF):0x60,                          # ¿ point interrogation renversé

                 'à':0x7F                                 # a accent grave
                }

def ASCIIToGSM3_38(sName):
    """ converts an ascii name string to a GSM 3.38 name string
        sample : "@£$èéùPascal" is converted to "\x00\x01\x02\x04\x05\x06"
        Input :
            - sName     = string containing the name
        Returns a string
    """

    gsmName =''
    for char in sName:
        if ((char >= "%") and (char <= "?")):
            gsmName += char
        elif ((char >= "A") and (char <= "Z")):
            gsmName += char
        elif ((char >= "a") and (char <= "z")):
            gsmName += char
        else:
            gsmName += chr(dic_GSM_3_38[char])
    return gsmName

#===============================================================================

dic_GSM_3_38_toAscii = { 0x00:'@',                                # @ At symbol
                 0x01:'£',                                # £ Britain pound symbol
                 0x02:'$',                                # $ Dollar symbol
                 0x03:chr(0xA5),                          # ¥ Yen symbol
                 0x04:'è',                                # è e accent grave
                 0x05:'é',                                # é e accent aigu
                 0x06:'ù',                                # ù u accent grave
                 0x07:chr(0xEC),                          # ì i accent grave
                 0x08:chr(0xF2),                          # ò o accent grave
                 0x09:chr(0xC7),                          # Ç C majuscule cedille
                 0x0A:chr(0x0A),                          # LF Line Feed
                 0x0B:chr(0xD8),                          # Ø O majuscule barré
                 0x0C:chr(0xF8),                          # ø o minuscule barré
                 0x0D:chr(0x0D),                          # CR Carriage Return
                 0x0E:chr(0xC5),                          # Å Angstroem majuscule
                 0x0F:chr(0xE5),                          # å Angstroem minuscule
                 0x11:'_',                                # underscore
                 0x1C:chr(0xC6),                          # Æ majuscule ae
                 0x1D:chr(0xE6),                          # æ minuscule ae
                 0x1E:chr(0xDF),                          # ß s dur allemand
                 0x1F:chr(0xC9),                          # É majuscule é

                 0x20:' ',
                 0x21:'!',
                 0x22:'\"',                               # guillemet
                 0x23:'#',
                 0x24:'¤',                                # ¤ carré

                 0x40:chr(0xA1),                          # ¡ point d'exclamation renversé
                 0x5B:chr(0xC4),                          # Ä majuscule A trema
                 0x5C:chr(0xD6),                          # Ö majuscule O trema
                 0x5D:chr(0xD1),                          # Ñ majuscule N tilda espagnol
                 0x5E:chr(0xDC),                          # Ü majuscule U trema
                 0x5F:chr(0xA7),                          # § signe paragraphe
                 0x60:chr(0xBF),                          # ¿ point interrogation renversé
                 0x7B:chr(0xE4),                          # ä minuscule a trema
                 0x7C:chr(0xF6),                          # ö minuscule o trema
                 0x7D:chr(0xF1),                          # ñ minuscule n tilda espagnol
                 0x7E:chr(0xFC),                          # ü minuscule u trema
                 0x7F:'à'                                 # a accent grave
                }

def GSM3_38ToASCII(gsmName):
    """ converts a GSM name string to ascii string using GSM 3.38 conversion table.

        - gsmName   = string containing the gsm name
        - Returns   = ascii string representation of the name.
        
        sample : "\x00\x01\x02\x04\x05\x06Pascal"
        	     is converted to "@£$èéùPascal"
    """

    sName = ""
    for i in gsmName:
        c = ord(i)
        if c == 0xFF: # End of name reached, treat an NULL character
            break
        elif dic_GSM_3_38_toAscii.has_key(c):
            sName += dic_GSM_3_38_toAscii[c]
        else:
            sName += i
    return sName

#===============================================================================

def ASCIIToPIN(sPIN):
    """ converts a PIN code string to a hex string with padding
        The PIN code string is padded with 'FF' until (8 - lg_sPIN).
        sample : "0000" is converted to "30303030FFFFFFFF"
        Input :
            - sPIN     = string containing the  cardholder code (PIN)
        
        Return a hex string of the PIN with FF padding.
    """
    from binascii import hexlify

    return hexlify(sPIN) + (8 - len(sPIN)) * 'FF'

#===============================================================================

def IntToHex(i, padchar='0', padlength=2):
    """ converts an integer to a hex string with padding
        sample : integer 12 is converted to string "0C"
    """
    res = hex(i).upper()[2:]
    while len(res) < padlength:
        res = "0" + res
    return res

#===============================================================================

def padString(s, length, padding="F"):
    l = length - len(s)
    return s + padding * l

#===============================================================================

def padFrontOfString(s, length, padding="0"):
    l = length - len(s)
    return padding * l + s

#===============================================================================

def removePadding(s, padding="FF"):
    i = len(padding)
    while s[-i:] == padding:
        s = s[:-i]
    return s

#===============================================================================

def stringToBitlist(data):
	"""Turn the string data, into a list of bits (1, 0)'s"""
	l = len(data) * 8
	result = [0] * l
	pos = 0
	for c in data:
		i = 7
		ch = ord(c)
		while i >= 0:
			if ch & (1 << i) != 0:
				result[pos] = 1
			else:
				result[pos] = 0
			pos += 1
			i -= 1

	return result

#===============================================================================

def bitlistToString(data):
	"""Turn the list of bits -> data, into a string"""
	result = ''
	pos = 0
	c = 0
	while pos < len(data):
		c += data[pos] << (7 - (pos % 8))
		if (pos % 8) == 7:
			result += chr(c)
			c = 0
		pos += 1

	return result
    