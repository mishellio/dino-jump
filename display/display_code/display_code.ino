/*
 * This sketch demonstrates the ability to set all channels of 
 * a TLC59116 driver simultaneously using the setPattern() function.
 */

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
int frame_count = 0;

// singular dino constants
// const int COLUMN = 8;
// const int ROW = 8;

// uint16_t binary[COLUMN] = {0};
// uint16_t binary2[COLUMN] = {0};
// uint16_t binary3[COLUMN] = {0};

// uint64_t binary_big[COLUMN] = {0};

bool detected = false;
long start_time = 0;
long s = 0;

void setup() {
  Wire.begin();
  Wire.setClock(400000);

  pinMode(RESET_PIN, OUTPUT);
  digitalWrite(RESET_PIN, LOW);
  delay(5);
  digitalWrite(RESET_PIN, HIGH);
  Serial.begin(9600);

  // sensor.setTimeout(500);
  // if (!sensor.init())
  // {
  //   Serial.println("Failed to detect and initialize sensor!");
  // }

  // sensor.setSignalRateLimit(0.4);
  // sensor.setMeasurementTimingBudget(20000);
  // sensor.startContinuous();

  // img_to_binary(DINO, binary);
  // img_to_binary_ranged(DINO_SCENE, binary, 0, 16);
  // img_to_binary_ranged(DINO_SCENE, binary2, 16, 32);
  // img_to_binary_ranged(DINO_SCENE, binary3, 32, 48);


  if (!manager.add(&board1))
    Serial.println("Failed to add board1");
  if (!manager.add(&board2))
    Serial.println("Failed to add board2");
  if (!manager.add(&board3))
    Serial.println("Failed to add board3");

  manager.begin();
  // board1.begin();
  // board2.begin();
  // board3.begin();
  Serial.println("setup() done");
}

void loop() {
  if (digitalRead(IR_PIN) == LOW) {

    binary_to_led(frame_count);
    frame_count++;
    if (frame_count == FRAMES_MAX) {
      frame_count = 0;
    }
    // delay(270); // add delay (100) to prevent double image on one side
    // add delay (200) so it only displays on 1 side
  }
}

// sample period for 50 rotations, return average
long get_half_period() {
  long period = 0;
  int num_rotation = 0;
  while (num_rotation < 25) {
      if (sensor.readRangeContinuousMillimeters() > 2000) {
        detected = false;
      }
      else if (!detected) {
        long end_time = micros()-start_time;
        Serial.println(end_time);
        if (end_time < 170000) {
          period += end_time;
          num_rotation += 1;
        }
        detected = true;
        start_time = micros();
      }
      if (sensor.timeoutOccurred()) { Serial.print(" GET FREQUENCY TIMEOUT"); }
  }
  return period/num_rotation;
}

void binary_to_led(int frame) {
  for(int col = 0; col < COLUMN; col++) {
    uint64_t binary = col_to_bin(FRAMES[frame], col);
    manager.setPattern(binary, 255);
  }
  manager.setPattern(0, 255);
}

// void binary_to_led_all() {
//   for(int col = 0; col < COLUMN; col++) {
//     board1.setPattern(binary[col], 255);
//     board2.setPattern(binary2[col], 255);
//     board3.setPattern(binary3[col], 255);
//   }
//   board1.setPattern(0, 255);
//   board2.setPattern(0, 255);
//   board3.setPattern(0, 255);
// }

uint64_t col_to_bin(const int img[][COLUMN], int col_num) {
  uint64_t binary = 0;
  for(int row = 0; row < ROW; row++) {
      uint64_t uint64 = img[row][col_num];
      binary |= uint64 << row;
    }
  return binary;
}

// void img_to_binary(const int img[][COLUMN], uint64_t bin[]) {
//   for(int col = 0; col < COLUMN; col++) {
//     for(int row = 0; row < ROW; row++) {
//       uint64_t uint64 = img[row][col];
//       bin[col] |= uint64 << row;
//     }
//   }
// }

// void img_to_binary_ranged(const int img[][COLUMN], uint16_t bin[], int row_start, int row_end) {
//   for(int col = 0; col < COLUMN; col++) {
//     for(int row = row_start; row < row_end; row++) {
//       bin[col] |= img[row][col] << row%16;
//     }
//   }
// }

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