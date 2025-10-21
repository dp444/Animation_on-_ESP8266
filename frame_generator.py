from PIL import Image
import os
import sys

def convert_image_to_c_array_mono(image_path, output_folder, target_width, target_height, invert=False):
    """
    Converts a single image file into a C-style 1-bit monochrome byte array.
    
    Args:
        image_path (str): Path to the input image file.
        output_folder (str): Directory where the .h file will be saved.
        target_width (int): Desired width to resize the image to.
        target_height (int): Desired height to resize the image to.
        invert (bool): If True, inverts pixels (white becomes black, black becomes white).
    """
    
    try:
        img = Image.open(image_path)
    except IOError:
        print(f"  Error: Cannot open image file {image_path}. Skipping.")
        return

    # Resize to target dimensions
    img = img.resize((target_width, target_height), Image.LANCZOS)
    
    # Convert to 1-bit black and white
    # Pillow's '1' mode converts to 1-bit pixels (0=black, 255=white)
    img = img.convert('1')
    
    # Extract base name for array and file naming
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    # Sanitize for C variable name (replace non-alphanumeric with underscore)
    array_name = ''.join(c if c.isalnum() else '_' for c in base_name) + "_map"
    
    # Pack 8 pixels into one byte, row by row (horizontal packing, MSB first)
    byte_array = bytearray()
    for y in range(target_height):
        for x_byte in range(target_width // 8):
            current_byte = 0
            for x_bit in range(8):
                x = x_byte * 8 + x_bit
                pixel = img.getpixel((x, y)) # 0 for black, 255 for white
                
                is_on = (pixel > 0) # True if white (or > 0), False if black (0)
                if invert:
                    is_on = not is_on # Flip if inversion is requested
                    
                if is_on:
                    # Set the bit (MSB first for Digole-style display drivers)
                    current_byte |= (1 << (7 - x_bit))
            
            byte_array.append(current_byte)
                
    # --- Write to output file ---
    output_filename = os.path.join(output_folder, f"{base_name}.h")
    try:
        with open(output_filename, 'w') as f:
            f.write(f"// Generated from: {os.path.basename(image_path)}\n")
            f.write(f"// Format: 1-bit Monochrome, Size: {target_width}x{target_height}\n")
            if invert:
                f.write(f"// Inverted: Yes (white pixels become 0, black become 1)\n")
            else:
                f.write(f"// Inverted: No (white pixels become 1, black become 0)\n")
            f.write(f"const unsigned char {array_name}[] = {{\n    ")
            
            for i, byte in enumerate(byte_array):
                f.write(f"0x{byte:02X}, ")
                if (i + 1) % 16 == 0: # 16 bytes per line for readability
                    f.write("\n    ")
            
            f.write("\n};")
            f.write(f"\n// Array size: {len(byte_array)} bytes\n")
        
        print(f"  Successfully converted '{os.path.basename(image_path)}' to '{base_name}.h'")

    except IOError:
        print(f"  Error: Cannot write to output file {output_filename}. Skipping.")

def batch_convert_images_to_c_array(input_folder, output_folder, target_width, target_height, invert=False):
    """
    Processes all image files in an input folder, converting them to C-style
    monochrome byte arrays and saving them to an output folder.
    """
    
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.")
        return
        
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: '{output_folder}'")

    print(f"\nStarting batch conversion from '{input_folder}' to '{output_folder}'...")
    print(f"Target dimensions: {target_width}x{target_height} (Monochrome)")
    print(f"Pixel Inversion: {'Enabled' if invert else 'Disabled'}")
    print("-" * 50)

    processed_count = 0
    supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif') # Add more if needed

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(supported_extensions):
            image_path = os.path.join(input_folder, filename)
            print(f"Processing: {filename}")
            convert_image_to_c_array_mono(image_path, output_folder, target_width, target_height, invert)
            processed_count += 1
        else:
            print(f"Skipping non-image file: {filename}")

    print("-" * 50)
    if processed_count == 0:
        print("No supported image files found in the input folder.")
    else:
        print(f"Batch conversion complete. Processed {processed_count} image(s).")

# --- --- --- --- --- --- --- --- --- ---
# --- HOW TO USE ---
# --- --- --- --- --- --- --- --- --- ---
if __name__ == "__main__":
    
    # --- CONFIGURE YOUR BATCH CONVERSION ---
    
    INPUT_IMAGE_FOLDER = "input_images"   # <--- Create this folder and put your images here
    OUTPUT_C_HEADER_FOLDER = "output_headers" # <--- This folder will be created for the .h files

    TARGET_WIDTH = 128
    TARGET_HEIGHT = 64
    
    # Set to True if your display expects 0 for 'on' pixels and 1 for 'off' pixels.
    # Standard is False (1 for 'on', 0 for 'off').
    INVERT_PIXELS = False 

    # Run the batch conversion
    batch_convert_images_to_c_array(
        INPUT_IMAGE_FOLDER, 
        OUTPUT_C_HEADER_FOLDER, 
        TARGET_WIDTH, 
        TARGET_HEIGHT,
        INVERT_PIXELS
    )