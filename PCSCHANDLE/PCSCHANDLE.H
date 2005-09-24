/* File : PCSCHandle.h */
#include "WinSCard.h"

#define DEBUG_PCSC			0

#define PCSC_INITIALISED	0
#define PCSC_OK				1
#define PCSC_ERROR			2

class PCSCHandle {
public:
  PCSCHandle();
  virtual ~PCSCHandle();
  char *getReaderName(int readerNumber);
  char *listAllReaders();
  long openSession(char *readerName, int protocol);
  long closeSession();
  char *getATR();
  char *getAttribute(int id);
  char *sendAPDU(char *pduString);
  long numberReaders;
  long status;
private:
  long refreshReaderNames();
  void freeReaderNameMemory();
  long beginTransaction();
  long endTransaction();
  byte * HexToBytes(const char *hexString, DWORD *pdulen);
  char * BytesToHex(byte *pdu, int pdulen);
  SCARDCONTEXT hSC;
  SCARDHANDLE  hCardHandle;
  LPTSTR readerNames;
};

void printDebug(const char *format, ...);
