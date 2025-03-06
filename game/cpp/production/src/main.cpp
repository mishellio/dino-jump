#include "game.hpp"
#include "terminal_display.hpp"

#include <atomic>
#include <iostream>
#include <mutex>
#include <thread>

const int SPEED = 10000;

std::atomic<char> curr_input{'\0'};
bool quit = false;

void input_thread_func() {
	while (!quit) {
		char key = read_key();
		curr_input.store(key);
	}
}

void player_input(Game &game) {
	char key = curr_input.load();
	Input_State input = NEUTRAL;
	if (key == 'w') {
		input = JUMP;
	} else if (key == 's') {
		input = DUCK;
	}
	game.input(input);
}

bool player_quit() {
	char key = curr_input.load();
	if (key == 'q') {
		return true;
	}
	return false;
}

void print_compressed_frame(Frame frame) {
	// Each column (uint64_t) takes at most 13 characters (16 - 4 for hex, 1 for comma)
	// 1 additional character for '\0'
	char buf[MAX_X * 13 + 1] = {0};
	frame.compressed_form(buf);
	std::cout << buf << std::endl;
}

int main() {
	Game game = Game();
	init_terminal();

	std::thread input_thread(input_thread_func);

	while (!game.get_collision()) {
		player_input(game);
		game.update_obstacles();
		game.update_frame();
		// print_frame(game.get_frame().to_uint8_array<MAX_Y>());
		print_compressed_frame(game.get_frame());
		usleep(SPEED);
	}
	// If piping output to python script, we don't expect any player input from terminal
	// So we sleep for 1 second (to see the death screen) then quit the program.
	// This is done before printing the score as the python script terminates right after that.
	sleep(5);
	quit = true;

	std::cout << "Score: " << game.get_score() << "\n";
	std::cout << "Press Q to quit!\n";

	// while (!quit) {
	// 	quit = player_quit();
	// }

	input_thread.join();
	reset_terminal();
}
