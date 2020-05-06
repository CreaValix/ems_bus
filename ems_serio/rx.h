void rx_packet(int *abort);
void rx_done();

extern enum STATE state;
extern uint8_t read_expected[HDR_LEN];
extern struct timeval got_bus;
int rx_wait();
int rx_break();
