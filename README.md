Arduino OLED Animation Builder
This project provides a complete Python-based workflow for converting an animated GIF into an Arduino sketch, optimized for display on an SSD1306 128x64 OLED using the Adafruit GFX and SSD1306 libraries.

The workflow automates the typically manual and tedious process of frame extraction, image conversion to C-style byte arrays, and Arduino code generation.

Workflow Overview
The entire process is orchestrated by three Python scripts:

image_splitter.py: Extracts individual frames from an animated GIF, handling GIF optimization techniques to ensure each frame is correctly composited.

frame_generator.py: Converts the extracted image frames (e.g., .gif files) into 1-bit monochrome C-style byte array header files (.h), suitable for embedding in Arduino sketches.

code_generator.py: Takes the generated .h files and a user-defined Arduino template sketch (.ino), then automatically constructs the final Arduino sketch, injecting all frame data (marked with PROGMEM) and generating the loop() display logic.

Features
GIF Frame Splitting: Robustly extracts and composites frames from optimized GIFs, ensuring visual fidelity.

Image to C Array Conversion: Transforms image frames into efficient 1-bit monochrome byte arrays.

Automatic Arduino Sketch Generation:

PROGMEM Integration: All frame data is automatically placed in program memory, conserving precious RAM on your microcontroller.

Dynamic Loop Generation: The loop() function is automatically populated with display.drawBitmap() calls for each frame.

Template-Based Structure: Allows for easy customization of the base Arduino sketch.

Intelligent Naming: Maps sequential frame files (e.g., frame_000.h) to appropriately named Arduino variables (e.g., Frame1, Frame2).

Prerequisites
Python 3: Required to run all build scripts.

Install the Pillow library: pip install Pillow

Arduino IDE: For compiling and uploading the final sketch to your microcontroller.

Arduino Libraries: Install these via the Arduino IDE's Library Manager:

Adafruit_GFX

Adafruit_SSD1306

Project Structure
Organize your project files as follows:

arduino_animation_builder/
├── input_videos/
│   └── your_animation.gif      # Your source animated GIF goes here.(rename it test.gif)
│
├── input_images/
│   └── (Generated: Extracted GIF frames will be saved here)
│
├── output_headers/
│   └── (Generated: C-style header files (.h) will be saved here)
│
├── template/
│   └── animation.ino           # Your custom template Arduino sketch(or use the one provided)
│
├── animation_updated/
│   └── (Generated: The final .ino sketch will be saved here)
│
├── image_splitter.py           # Script to split GIFs into frames
├── frame_generator.py          # Script to convert frames to .h files
└── code_generator.py      # Script to build the final Arduino .ino sketch
Step-by-Step Guide
Follow these steps sequentially to convert your animated GIF into an Arduino animation sketch.

Step 1: Prepare Your Arduino Template Sketch
Create or modify the Template/animation.ino file. It must contain the following placeholders for the build_animation_ino.py script to inject code:

// __FRAME_DEFINITIONS__

// __FRAME_LOOP__

Refer to the templet/animation.ino file in this repository for the required structure.

Step 2: Split GIF into Individual Frames
Place your animated GIF (e.g., your_animation.gif) into the input_videos/ folder.

Then, run the image_splitter.py script from your project's root directory:

Bash

python3 image_splitter.py
This script will:

Create the input_images/ folder if it doesn't exist.

Extract each frame from your GIF and save it as frame_000.gif, frame_001.gif, etc., into input_images/.

Handle GIF optimization and disposal methods to ensure correct frame compositing.

Refer to image_splitter.py for its full code and configuration options.

Step 3: Convert Image Frames to C Header Files
Next, run the frame_generator.py script:

Bash

python3 frame_generator.py
This script will:

Read all .gif files from input_images/.

Create the output_headers/ folder if it doesn't exist.

Convert each image frame into a 1-bit monochrome C-style byte array.

Save these arrays as header files (e.g., frame_000.h, frame_001.h) into output_headers/.

Refer to frame_generator.py for its full code and configuration options (e.g., TARGET_WIDTH, TARGET_HEIGHT, INVERT_PIXELS).

Step 4: Build the Final Arduino Sketch
Finally, run the build_animation_ino.py script:

Bash

python3 build_animation_ino.py
This script will:

Read the generated .h files from output_headers/.

Read your template from templet/animation.ino.

Create the animation_updated/ folder if it doesn't exist.

Generate the complete Arduino sketch as animation_updated/animation_updated.ino, with all frame definitions (using PROGMEM) and the display loop.

Refer to build_animation_ino.py for its full code and configuration options.

Step 5: Compile and Upload to Arduino
Open the newly generated animation_updated/animation_updated.ino file in your Arduino IDE.

Select your specific Arduino board and the correct COM port from the Tools menu.

Click the Upload button in the Arduino IDE to compile the sketch and flash it to your microcontroller.

Your SSD1306 OLED display should now spring to life with your custom animation!