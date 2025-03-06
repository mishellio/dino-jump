#ifndef TERMINAL_DISPLAY_HPP
#define TERMINAL_DISPLAY_HPP

#include "constants.hpp"

#include <array>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

void init_terminal();
void reset_terminal();
char read_key();
void print_frame(const std::array<std::array<uint8_t, MAX_X>, MAX_Y> &frame);

#endif // TERMINAL_DISPLAY_HPP
