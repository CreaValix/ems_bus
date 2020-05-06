#include <pthread.h>

#include "defines.h"

extern struct STATS stats;
extern int logging;
extern pthread_t readloop;

int start(char *);
int stop();
void print_packet(int, int, uint8_t *, size_t len);
