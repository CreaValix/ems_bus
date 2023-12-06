CC=gcc
CFLAGS=-I. -std=c11 -Wall -Wextra -Werror -Wstrict-aliasing -fmax-errors=5 \
	-Wunreachable-code -Wcast-align -Wcast-qual -Wdisabled-optimization -Wformat=2 \
	-Wlogical-op -Wmissing-include-dirs -Wredundant-decls -Wshadow \
	-Wstrict-overflow=2 -Wswitch-default -Wundef -fdiagnostics-show-option -O2
LDFLAGS=-lrt -lpthread
OBJS = crc.o ems_serio.o queue.o rx.o serial.o tx.o

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

ems_serio: $(OBJS)
	$(CC) -o $@ $^ $(CFLAGS) $(LDFLAGS)

clean:
	rm *.o ems_serio
