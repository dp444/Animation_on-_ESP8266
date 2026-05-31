# 🧠 Automatic ESP8266 OLED Animation Builder

![Images/IMG1.jpeg](https://raw.githubusercontent.com/dp444/Animation_on-_ESP8266/main/Images/IMG1.jpeg)

### 🖥️ New Modern Desktop GUI
![Images/IMG2.jpeg](https://raw.githubusercontent.com/dp444/Animation_on-_ESP8266/main/Images/IMG2.jpeg)

- Convert any animated GIF into a complete Arduino sketch for SSD1306 128x64 OLED displays — automatically!
- This Python-based workflow handles frame extraction, image conversion, and Arduino code generation using the Adafruit GFX and SSD1306 libraries. It now features a modern desktop GUI to manage the entire pipeline with a single click.
- Refer to sites below to learn interfacing of esp8266,oled display and manually creating animations before diving into this.
1. https://randomnerdtutorials.com/esp8266-0-96-inch-oled-display-with-arduino-ide/
2. https://www.instructables.com/Running-Animations-on-OLED-DISPLAY-SSD1306/

### 🚀 Features

🖥️ **Modern Desktop GUI:** Manage dimensions, invert pixels, and build the code from a clean UI.

🎞️ **GIF Frame Splitting:** Extracts and composites frames from optimized GIFs.

🧩 **Image → C Array:** Converts frames into 1-bit monochrome byte arrays.

🧹 **Auto-Cleanup:** Automatically deletes temporary image and header folders to keep your workspace clean.

### ⚙️ Auto Arduino Sketch Builder:

Stores frames in PROGMEM (program memory).

Generates dynamic display loops using display.drawBitmap().

Supports template-based customization.

Allows 1-click copying to clipboard or opening directly in your code editor.

### ⚙️ Prerequisites

#### Python 3

```bash
pip install Pillow
```
*(Note for Linux users: If the GUI doesn't open, you may need to run `sudo apt install python3-tk python3-pil`)*

#### Arduino IDE

#### Arduino Libraries:

Adafruit_GFX

Adafruit_SSD1306

### 🧭 Step-by-Step Guide

#### Method A: Using the GUI (Recommended)

**1. Launch the App**
Run the graphical interface from your terminal:
```bash
python3 gui.py
```

**2. Configure & Run**
- Click **Browse** to select your source `.gif` file.
- Set your target **Width** and **Height** (default is 128x64).
- Click **▶ RUN FULL PIPELINE**.

**3. Upload to ESP8266**
Once finished, click the **Open in Editor** or **Copy to Clipboard** button at the bottom of the app. Paste the code into the Arduino IDE, select your board and port, then upload!

---

#### Method B: Manual Command Line

#### 1. Split GIF

Place your .gif in input_videos/ and run:

```bash
python3 image_splitter.py
```

#### 2. Convert Frames

Generate 1-bit C header files:

```bash
python3 frame_generator.py
```

#### 3. Build Final Sketch

Assemble everything into one .ino:

```bash
python3 code_generator.py
```

#### 4. Upload to ESP8266

Open animation_updated/animation_updated.ino in Arduino IDE, select your board and port, then upload — your OLED will animate!
