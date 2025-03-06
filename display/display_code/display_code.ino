#include <TLC59116.h>
#include <TLC59116Manager.h>
#include "images.h"
#include "frames.hpp"

#include <VL53L0X.h>
VL53L0X sensor;

// #define RESET_PIN D7
#define RESET_PIN D7
#define IR_PIN D8

TLC59116 board1(0b1100000, true);
TLC59116 board2(0b1100001, true);
TLC59116 board3(0b1100010, true);
// TLC59116 board4(0b1100011, true);
// TLC59116 board5(0b1100100, true);
// TLC59116 board6(0b1100101, true);

// 2nd board as 1, 2, 3
// TLC59116 board1(0b1100011, true);
// TLC59116 board2(0b1100100, true);
// TLC59116 board3(0b1100101, true);

TLC59116Manager manager;

// dino frame constants
const int COLUMN = SCREEN_WIDTH;
const int ROW = SCREEN_HEIGHT;
const int FRAMES_MAX = FRAME_NUM;
int frame_num = 0;

// singular dino constants
// const int COLUMN = 8;
// const int ROW = 8;

bool detected = false;
long start_time = 0;
// long s = 0;

void setup() {
  Wire.begin();
  Wire.setClock(400000);

  pinMode(RESET_PIN, OUTPUT);
  digitalWrite(RESET_PIN, LOW);
  delay(5);
  digitalWrite(RESET_PIN, HIGH);
  Serial.begin(9600);

  if (!manager.add(&board1))
    Serial.println("Failed to add board1");
  if (!manager.add(&board2))
    Serial.println("Failed to add board2");
  if (!manager.add(&board3))
    Serial.println("Failed to add board3");

  manager.begin();
  Serial.println("setup() done");
  start_time = micros();
}

void loop() {
  if (digitalRead(IR_PIN) == LOW) {
    bin_to_led(frame_num);
    if (++frame_num == FRAMES_MAX) {
      frame_num = 0;
    }
    // delay(270); // add delay (100) to prevent double image on one side
    // add delay (200) so it only displays on 1 side
  }
}

void bin_to_led(int frame_num) {
  for(int col = 0; col < COLUMN; col++) {
    uint64_t bin = col_to_bin(FRAMES[frame_num], col);
    double col_delay = get_col_delay(bin, frame_num, col);
    manager.setPattern(bin, 255);
    delayMicroseconds(300 * col_delay);
  }
  manager.setPattern(0, 255);
}

double get_col_delay(uint64_t bin, int frame_num, int col){
  uint64_t prev_bin = frame_num == 0 ? 0 : col_to_bin(FRAMES[frame_num - 1], col);
  uint64_t xor_bin = prev_bin ^ bin;
  int bits_changed = 0;
  while (xor_bin) {
    bits_changed += (xor_bin & 1);
    xor_bin >>= 1;
  }
  return (48 - bits_changed) / 48.0;
}

uint64_t col_to_bin(const int img[][COLUMN], int col_num) {
  uint64_t bin = 0;
  for(int row = 0; row < ROW; row++) {
      // uint64_t uint_64 = img[row][col_num];
      bin |= (uint64_t)img[row][col_num] << row;
    }
  return bin;
}

void get_half_period(){
  if (digitalRead(IR_PIN) == HIGH) {
    detected = false;
  }
  else if (!detected) {
    detected = true;
    int end_time = micros() - start_time;
    start_time = micros();
    Serial.print("p: ");
    Serial.println(end_time);
  }
}

// lights up all leds
void sanity_check_leds() {
  board1.setPattern(0xFFFF, 255);
  board2.setPattern(0xFFFF, 255);
  board3.setPattern(0xFFFF, 255);
  // board4.setPattern(0xFFFF, 255);
  // board5.setPattern(0xFFFF, 255);
  // board6.setPattern(0xFFFF, 255);
}

// checks all elements in an array
void sanity_check_array(int array[]) {
  for (int i = 0; i < COLUMN; i++) {
    Serial.print("sanity check: ");
    Serial.println(array[i]);
  }
}