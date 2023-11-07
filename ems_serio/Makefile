CC=gcc
#CFLAGS=-I. -std=c11 -Wall -Wextra -Werror -Wstrict-aliasing -pedantic -fmax-errors=5 \
#	-Wunreachable-code -Wcast-align -Wcast-qual -Wdisabled-optimization -Wformat=2 \
#	-Winit-self -Wlogical-op -Wmissing-include-dirs -Wredundant-decls -Wshadow \
#	-Wstrict-overflow=2 -Wswitch-default -Wundef -Wno-unused -Wno-variadic-macros \
#	-Wno-parentheses -fdiagnostics-show-option -O2
CFLAGS=-I. -std=c11 -Wall -Wextra -Werror -Wstrict-aliasing -fmax-errors=5 \
	-Wunreachable-code -Wcast-align -Wcast-qual -Wdisabled-optimization -Wformat=2 \
	-Winit-self -Wlogical-op -Wmissing-include-dirs -Wredundant-decls -Wshadow \
	-Wstrict-overflow=2 -Wswitch-default -Wundef -Wno-unused \
	-Wno-parentheses -fdiagnostics-show-option -Wno-unused-result -O2
LDFLAGS=-lrt -lpthread
OBJS = crc.o ems_serio.o queue.o rx.o serial.o tx.o

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

ems_serio: $(OBJS)
	$(CC) -o $@ $^ $(CFLAGS) $(LDFLAGS)

clean:
	rm *.o ems_serio
