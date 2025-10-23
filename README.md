# 🧠 Automatic ESP8266 OLED Animation Builder

[Images/IMG1.jpeg](https://github.com/dp444/Animation_on-_ESP8266/blob/main/Images/IMG1.jpeg

- Convert any animated GIF into a complete Arduino sketch for SSD1306 128x64 OLED displays — automatically!
- This Python-based workflow handles frame extraction, image conversion, and Arduino code generation using the Adafruit GFX and SSD1306 libraries.
- Refer to sites below to learn interfacing of esp8266,oled display and manually creating animations before diving into this.
1. https://randomnerdtutorials.com/esp8266-0-96-inch-oled-display-with-arduino-ide/
2. https://www.instructables.com/Running-Animations-on-OLED-DISPLAY-SSD1306/

### 🚀 Features

🎞️ GIF Frame Splitting: Extracts and composites frames from optimized GIFs.

🧩 Image → C Array: Converts frames into 1-bit monochrome byte arrays.

### ⚙️ Auto Arduino Sketch Builder:

Stores frames in PROGMEM (program memory).

Generates dynamic display loops using display.drawBitmap().

Supports template-based customization.


### ⚙️ Prerequisites

#### Python 3

```
 pip install Pillow
```

#### Arduino IDE

#### Arduino Libraries:

Adafruit_GFX

Adafruit_SSD1306

### 🧭 Step-by-Step Guide


####  1. Split GIF

Place your .gif in input_videos/ and run:

```
python3 image_splitter.py
```

#### 2. Convert Frames

Generate 1-bit C header files:

```
python3 frame_generator.py
```
####  3. Build Final Sketch

Assemble everything into one .ino:

```
python3 code_generator.py
```

#### 4. Upload to ESP8266

Open animation_updated/animation_updated.ino in Arduino IDE,
select your board and port, then upload — your OLED will animate!
