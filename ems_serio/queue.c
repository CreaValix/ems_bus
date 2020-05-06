#include <mqueue.h>

#include "defines.h"

mqd_t tx_queue;
mqd_t rx_queue;

void setup_queue(mqd_t *queue, char *name) {
    struct mq_attr queue_attr;
    queue_attr.mq_maxmsg = 32;
    queue_attr.mq_msgsize = MAX_PACKET_SIZE;
    *queue = mq_open(name, O_RDWR | O_NONBLOCK | O_CREAT, 0666, queue_attr);
}

void close_queues() {
    mq_close(rx_queue);
    mq_close(tx_queue);
}
