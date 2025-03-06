#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

#include "emulator.hpp"
#include "frames.hpp"

const char SHOW_CURSOR[] = "\x1b[?25h";
const char HIDE_CURSOR[] = "\x1b[?25l";
const char MOVE_CURSOR_HOME[] = "\x1b[H";
const char CLEAR_SCREEN[] = "\x1b[2J";

struct termios orig_termios;

void die(const char *s);
void reset_terminal();

void print_frame(const int screen[SCREEN_HEIGHT][SCREEN_WIDTH]) {
	// Note that the █ character takes two bytes to store, so the buffer length
	// needs to be big
	const int BUF_LEN = SCREEN_HEIGHT * SCREEN_WIDTH * 3;

	char buf[BUF_LEN] = {0};

	sprintf(buf + strlen(buf), HIDE_CURSOR);
	sprintf(buf + strlen(buf), MOVE_CURSOR_HOME);
	for (int y = 0; y < SCREEN_HEIGHT; y++) {
		for (int x = 0; x < SCREEN_WIDTH; x++) {
			if (screen[y][x] == 1) {
				sprintf(buf + strlen(buf), "█");
			} else {
				sprintf(buf + strlen(buf), ".");
			}
		}
		sprintf(buf + strlen(buf), "\r\n");
	}

	printf("%s", buf);
	fflush(stdout);
}

void die(const char *s) {
	write(STDOUT_FILENO, CLEAR_SCREEN, 4);
	write(STDOUT_FILENO, MOVE_CURSOR_HOME, 3);
	perror(s);
	exit(1);
}

// Returns a character read from stdin. If there are none, returns '\0'
char read_key() {
	char key = '\0';
	// Note that read can return 0 because of the terminal settings
	int rv = read(STDIN_FILENO, &key, 1);

	if (rv == -1 && errno != EAGAIN) {
		die("read");
	}

	return key;
}

void reset_terminal() {
	if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios) == -1)
		die("tcsetattr");
	printf(CLEAR_SCREEN);
	printf(MOVE_CURSOR_HOME);
	printf(SHOW_CURSOR);
	fflush(stdout);
}

// Does some magic so that the terminal acts like a screen
void init_terminal() {
	if (tcgetattr(STDIN_FILENO, &orig_termios) == -1)
		die("tcgetattr");
	atexit(reset_terminal);

	struct termios new_termios = orig_termios;

	// Disable echoing, and read input byte by byte instead of line by line
	new_termios.c_lflag &= ~(ECHO | ICANON);
	// Set minimum number of bytes before read() returns
	new_termios.c_cc[VMIN] = 0;
	// Set maximum amount of time before read() returns
	new_termios.c_cc[VTIME] = 0;

	if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &new_termios) == -1)
		die("tcsetattr");
}
