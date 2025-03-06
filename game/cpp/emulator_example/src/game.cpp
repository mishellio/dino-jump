#include <stdlib.h>
#include <unistd.h>

#include "emulator.hpp"
#include "frames.hpp"

int main() {
	init_terminal();

	// The pause variable is purely for showing that the spacebar can be used
	// for input. It is not needed for the actual game
	bool pause = false;
	int f = 0;
	while (true) {
		char key = read_key();
		if (key == 'q') {
			exit(0);
		}
		if (key == ' ') {
			pause = !pause;
		}

		if (!pause) {
			f = (f + 1) % FRAME_NUM;
		}
		print_frame(FRAMES[f]);
		usleep(10000);
	}
	return 0;
}
