// PCSCHandle.cpp: implementation of the PCSCHandle class.
//
//////////////////////////////////////////////////////////////////////

#include <stdio.h>
#include "PCSCHandle.h"

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

PCSCHandle::PCSCHandle()
{
	LONG lReturn;

	// Initialise variables
	readerNames = NULL;
	numberReaders = 0;
	status = PCSC_INITIALISED;

	// Establish the context.
	lReturn = SCardEstablishContext(SCARD_SCOPE_SYSTEM,
									NULL,
									NULL,
									&hSC);
	if ( SCARD_S_SUCCESS != lReturn )
		printDebug("Failed SCardEstablishContext: %X\n", lReturn);
	else
		if ( refreshReaderNames() == SCARD_S_SUCCESS )
			status = PCSC_OK;
		else
			status = PCSC_ERROR;
}

PCSCHandle::~PCSCHandle()
{
	freeReaderNameMemory();
	SCardReleaseContext(hSC);
}

void PCSCHandle::freeReaderNameMemory()
{
	LONG            lReturn;

	if (readerNames != NULL)
	{
		lReturn = SCardFreeMemory( hSC,
								   readerNames );
		if ( SCARD_S_SUCCESS != lReturn )
			printDebug("Failed SCardFreeMemory: %X\n", lReturn);
	}
	readerNames = NULL;
	numberReaders = 0;
}

long PCSCHandle::refreshReaderNames()
{
	LPTSTR          pReader;
	LONG            lReturn;
	DWORD           cch = SCARD_AUTOALLOCATE;

	// Free any previously used memory
	freeReaderNameMemory();

	// Retrieve the list the readers.
	lReturn = SCardListReaders(hSC,
							   NULL,
							   (LPTSTR)&readerNames,
							   &cch );
	if (lReturn != SCARD_S_SUCCESS)
	{
		printDebug("Failed SCardListReaders: %X\n", lReturn);
		return lReturn;
	}

	// A double-null terminates the list of reader names.
	pReader = readerNames;
	while ( '\0' != *pReader )
	{
		numberReaders++;
		pReader = pReader + strlen(pReader) + 1;
	}
	return SCARD_S_SUCCESS;
}

char * PCSCHandle::getReaderName(int readerNumber)
{
	int i;
	LPTSTR          pReader;

	if ((readerNumber >= 1) && (readerNumber <= numberReaders))
	{
		i = 0;
		pReader = readerNames;
		while ( '\0' != *pReader )
		{
			if (++i == readerNumber)
				return pReader;
			pReader = pReader + strlen(pReader) + 1;
		}
	}
	return "";
}

char * PCSCHandle::listAllReaders()
{
	int i;
	LPTSTR          pReader;
	static char		readerNameList[1024];

	*readerNameList = '\0';

	if ( refreshReaderNames() == SCARD_S_SUCCESS && numberReaders >= 0)
	{
		i = 0;
		pReader = readerNames;
		while ( '\0' != *pReader )
		{
			strcat(readerNameList, pReader);
			strcat(readerNameList, "\t");
			pReader = pReader + strlen(pReader) + 1;
		}
	}

	return readerNameList;
}

long PCSCHandle::openSession(char *readerName, int protocol)
{
	LONG            lReturn;
	DWORD           dwAP;

	lReturn = SCardConnect( hSC, 
							readerName,
							SCARD_SHARE_SHARED,
							protocol,
							&hCardHandle,
							&dwAP );
	if ( SCARD_S_SUCCESS != lReturn )
	{
		printDebug("Failed SCardConnect: %X\n", lReturn);
		return -1;
	}

	return 0;
}

long PCSCHandle::closeSession()
{
	LONG            lReturn;

	lReturn = SCardDisconnect(hCardHandle, SCARD_UNPOWER_CARD);
	if ( SCARD_S_SUCCESS != lReturn )
	{
		printDebug("Failed SCardDisconnect: %X\n", lReturn);
		return -1;
	}
	return 0;
}

char * PCSCHandle::getATR()
{
	return getAttribute(SCARD_ATTR_ATR_STRING);
}

char * PCSCHandle::getAttribute(int id)
{
	LPBYTE   pbAttr = NULL;
	DWORD    cByte = SCARD_AUTOALLOCATE;
	LONG     lReturn;
	char *	 buf;

	lReturn = SCardGetAttrib(hCardHandle,
							 id,
							 (LPBYTE)&pbAttr,
							 &cByte);
	if ( SCARD_S_SUCCESS != lReturn )
	{
		printDebug("SCardGetAttrib() for attribute %X failed: %X\n", id, lReturn);
		return "";
	}

	buf = BytesToHex(pbAttr, cByte);
	// Free memory that was used
	lReturn = SCardFreeMemory( hSC, pbAttr );

	return buf;
}

char * PCSCHandle::sendAPDU(char *pduString)
{
	long     lReturn;
	//byte	 pbSend[256];
	byte	*pbSend;
	byte	 pbRecv[256];
	DWORD	 dwSend;
	DWORD	 dwRecv;

	beginTransaction();

	printDebug("In ) %s\n", pduString);
	pbSend = HexToBytes(pduString, &dwSend);

	dwRecv = 255;
	lReturn = SCardTransmit(hCardHandle,
							SCARD_PCI_T0,
							pbSend,
							//7,
							dwSend,
							NULL,
							pbRecv,
							&dwRecv );
	if ( SCARD_S_SUCCESS != lReturn )
	{
		printDebug("Failed SCardTransmit\n");
		return "";
	}

	endTransaction();

	printDebug("Out) %s\n", BytesToHex(pbRecv, dwRecv));
	return BytesToHex(pbRecv, dwRecv);
}

long PCSCHandle::beginTransaction()
{
	LONG     lReturn;

	lReturn = SCardBeginTransaction( hCardHandle );
	if ( SCARD_S_SUCCESS != lReturn )
	{
		printDebug("Failed SCardBeginTransaction: %X\n", lReturn);
		return -1;
	}
	return 0;
}

long PCSCHandle::endTransaction()
{
	LONG     lReturn;

	lReturn = SCardEndTransaction( hCardHandle, SCARD_LEAVE_CARD );
	if ( SCARD_S_SUCCESS != lReturn )
	{
		printDebug("Failed SCardEndTransaction: %X\n", lReturn);
		return -1;
	}
	return 0;
}

byte * PCSCHandle::HexToBytes(const char *hexString, DWORD *pdulen)
{
	static byte pdu[256];
	unsigned int i, j;
	char c;

	for (i=0, j=0; i < strlen(hexString); i+=2, j++)
	{
		c = toupper(hexString[i]);
		if (c >= '0' && c <= '9')
			pdu[j] = (c - '0') << 4;
		else
			pdu[j] = (c - 'A' + 10) << 4;

		c = toupper(hexString[i+1]);
		if (c >= '0' && c <= '9')
			pdu[j] += c - '0';
		else
			pdu[j] += c - 'A' + 10;
	}

	*pdulen = j;
	//for (i=0; i < j; i++)
	//	printDebug("%x", pdu[i]);
	//printDebug("%s\n", BytesToHex(pdu, j));
	return pdu;
}

char * PCSCHandle::BytesToHex(byte *pdu, int pdulen)
{
	static char hexString[512];
	int i, j;
	char c;

	for (i=0, j=0; i < pdulen; i++, j+=2)
	{
		c = (pdu[i] >> 4) & 0xF;
		if (c <= 9)
			hexString[j] = c + '0';
		else
			hexString[j] = c + 'A' - 10;

		c = pdu[i] & 0xF;
		if (c <= 9)
			hexString[j+1] = c + '0';
		else
			hexString[j+1] = c + 'A' - 10;
	}

	hexString[j] = '\0';
	return hexString;
}

void printDebug(const char *format, ...)
{
	va_list args;

	if ( format && DEBUG_PCSC != 0 )
	{
		va_start(args, format);  
		vfprintf(stderr, format, args);
		va_end(args);
	}
}
