#include <mqueue.h>

extern mqd_t rx_queue;
extern mqd_t tx_queue;

void setup_queue(mqd_t *, char *);
void close_queues();
