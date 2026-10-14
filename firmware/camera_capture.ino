#include "OV7670.h"
#include "BMP.h"

const int SIOD = 21, SIOC = 22;
const int VSYNC = 12, HREF = 13;
const int XCLK = 23, PCLK = 14;

const int D0 = 15, D1 = 33;
const int D2 = 4,  D3 = 16;
const int D4 = 17, D5 = 25;
const int D6 = 32, D7 = 26;

OV7670* camera = nullptr;
unsigned char bmpHeader[BMP::headerSize];

void setup() {
  Serial.begin(115200);
  delay(1500);

  camera = new OV7670(
    OV7670::Mode::QQVGA_RGB565,
    SIOD, SIOC, VSYNC, HREF, XCLK, PCLK,
    D0, D1, D2, D3, D4, D5, D6, D7
  );

  BMP::construct16BitHeader(
    bmpHeader, camera->xres, camera->yres
  );

  Serial.println("READY");
}

void loop() {
  if (!Serial.available()) return;

  char command = Serial.read();
  if (command != 'C' && command != 'c') return;

  camera->oneFrame();

  const uint32_t frameSize =
    (uint32_t)camera->xres * camera->yres * 2;
  const uint32_t totalSize =
    BMP::headerSize + frameSize;

  Serial.printf("IMG:%lu\n", (unsigned long)totalSize);
  Serial.flush();

  Serial.write(bmpHeader, BMP::headerSize);

  const uint8_t* frame = camera->frame;
  uint32_t offset = 0;

  while (offset < frameSize) {
    size_t count = frameSize - offset;
    if (count > 512) count = 512;

    size_t written = Serial.write(frame + offset, count);
    if (written == 0) break;

    offset += written;
  }

  Serial.flush();
}
