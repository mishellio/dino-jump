#ifndef EMULATOR_HPP
#define EMULATOR_HPP

#include "frames.hpp"

char read_key();
void init_terminal();
void print_frame(const int screen[SCREEN_HEIGHT][SCREEN_WIDTH]);

#endif // EMULATOR_HPP
