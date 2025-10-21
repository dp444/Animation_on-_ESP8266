🧠 Automatic ESP8266 OLED Animation Builder

Convert any animated GIF into a complete Arduino sketch for SSD1306 128x64 OLED displays — automatically!
This Python-based workflow handles frame extraction, image conversion, and Arduino code generation using the Adafruit GFX and SSD1306 libraries.
Refer to sites belowto learn interfacing of esp8266,oled display and manually creating animations before diving into this.
https://randomnerdtutorials.com/esp8266-0-96-inch-oled-display-with-arduino-ide/
https://www.instructables.com/Running-Animations-on-OLED-DISPLAY-SSD1306/

🚀 Features

🎞️ GIF Frame Splitting: Extracts and composites frames from optimized GIFs.

🧩 Image → C Array: Converts frames into 1-bit monochrome byte arrays.

⚙️ Auto Arduino Sketch Builder:

Stores frames in PROGMEM (program memory).

Generates dynamic display loops using display.drawBitmap().

Supports template-based customization.

📁 Project Structure
Animation_on_ESP8266/
├── input_videos/                             # Your source GIF(rename your GIF file to test.gif)
├── input_images/                             # (Generated) Extracted frames
├── output_headers/                           # (Generated) .h files for frames
├── Template/animation.ino                    # Template Arduino sketch
├── animation_updated/animation_updated.ino   # (Generated) Final Arduino sketch
├── image_splitter.py                         # Extracts GIF frames
├── frame_generator.py                        # Converts frames to .h files
└── code_generator.py                         # Builds final Arduino sketch

⚙️ Prerequisites

Python 3

Pillow → pip install Pillow

Arduino IDE

Arduino Libraries:

Adafruit_GFX

Adafruit_SSD1306

🧭 Step-by-Step Guide


2️⃣ Split GIF

Place your .gif in input_videos/ and run:

python3 image_splitter.py

3️⃣ Convert Frames

Generate 1-bit C header files:

python3 frame_generator.py

4️⃣ Build Final Sketch

Assemble everything into one .ino:

python3 code_generator.py

5️⃣ Upload to ESP8266

Open animation_updated/animation_updated.ino in Arduino IDE,
select your board and port, then upload — your OLED will animate!
