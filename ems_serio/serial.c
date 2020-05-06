#define _GNU_SOURCE 1

#include <termios.h>
#include <unistd.h>
#include <fcntl.h>

int port;
tcflag_t tcflag_normal;
tcflag_t tcflag_parity;
struct termios tios;

int open_serial(char *tty_path) {
    // Opens a raw serial with parity marking enabled
    int ret;

    port = open(tty_path, O_RDWR | O_NOCTTY);
    if (port < 0) {
        return(port);
    }

    ret = tcgetattr(port, &tios);
    if (ret != 0) {
        return(ret);
    }

    // Raw mode: Noncanonical mode, no input processing, no echo, no signals, no modem control.
    tios.c_cflag &= ~HUPCL;
    tios.c_cflag |= (CLOCAL | CREAD);

    tios.c_lflag &= ~(ICANON | ECHO | ECHOE | ECHOK | ECHONL | ISIG | IEXTEN |
                      ECHOPRT | ECHOCTL | ECHOKE);
    tios.c_oflag &= ~(OPOST | ONLCR | OCRNL);
    tios.c_iflag &= ~(INLCR | IGNCR | ICRNL | IGNBRK | BRKINT | IUCLC);

    // Enable parity marking.
    // This is important as each telegramme is terminated by a BREAK signal.
    // Without it, we could not distinguish between two telegrammes.
    tios.c_iflag |= PARMRK;

    // 9600 baud
    ret = cfsetispeed(&tios, B9600);
    ret |= cfsetospeed(&tios, B9600);
    if (ret != 0) {
        return(ret);
    }
    // 8 bits per character
    tios.c_cflag &= ~CSIZE;
    tios.c_cflag |= CS8;
    // No parity bit
    tios.c_iflag &= ~(INPCK | ISTRIP);
    tios.c_cflag &= ~(PARENB | PARODD | 010000000000);
    // One stop bit
    tios.c_cflag &= ~CSTOPB;
    // No hardware or software flow control
    tios.c_iflag &= ~(IXON | IXOFF);
    tios.c_cflag &= ~CRTSCTS;
    // Buffer
    tios.c_cc[VMIN] = 1;
    tios.c_cc[VTIME] = 0;
    ret = tcsetattr(port, TCSANOW, &tios);
    if (ret != 0) {
        return(ret);
    }
    tcflush(port, TCIOFLUSH);
    tcflag_normal = tios.c_cflag;
    tcflag_parity = (tcflag_normal | PARENB) & ~PARODD;
    return(0);
}

int close_serial() {
    return(close(port));
}

int set_parity(int enable) {
    tios.c_cflag = enable ? tcflag_parity : tcflag_normal;
    return(tcsetattr(port, TCSANOW, &tios));
}
