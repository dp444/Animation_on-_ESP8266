import re
import os
import sys
import glob # For finding files

# --- Configuration ---
TEMPLATE_INO_FILE = "Template/animation.ino"  # Path to your template INO file
HEADER_FOLDER_NAME = "output_headers"        # Folder with your frame_XXX.h files
OUTPUT_INO_FILE = "animation_updated/animation_updated.ino" # Output file path
FRAME_NUMBER_PADDING = 3                     # Digits for frame numbers (e.g., 3 for 000)
PLACEHOLDER_DEFINITIONS = "// __FRAME_DEFINITIONS__"
PLACEHOLDER_LOOP = "// __FRAME_LOOP__"
# --- End Configuration ---

# Construct full paths relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_INO_PATH = os.path.join(SCRIPT_DIR, TEMPLATE_INO_FILE)
HEADER_FOLDER_PATH = os.path.join(SCRIPT_DIR, HEADER_FOLDER_NAME)
OUTPUT_INO_PATH = os.path.join(SCRIPT_DIR, OUTPUT_INO_FILE)

# Ensure the output directory exists
OUTPUT_DIR = os.path.dirname(OUTPUT_INO_PATH)
if OUTPUT_DIR and not os.path.exists(os.path.join(SCRIPT_DIR, OUTPUT_DIR)):
    try:
        os.makedirs(os.path.join(SCRIPT_DIR, OUTPUT_DIR))
        print(f"Created output directory: '{OUTPUT_DIR}'")
    except OSError as e:
        print(f"Error creating output directory '{OUTPUT_DIR}': {e}")
        sys.exit(1)


def read_file_content(filepath):
    """Reads the entire content of a file."""
    content = None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"  [DEBUG] Read with UTF-8 FAILED for {filepath}. Trying Latin-1.")
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e_latin1:
            print(f"  [DEBUG] Error reading file {filepath} even with Latin-1: {e_latin1}")
            return None
    except IOError as e_io:
        print(f"  [DEBUG] Error reading file {filepath}: {e_io}")
        return None
    except Exception as e_other:
        print(f"  [DEBUG] An unexpected error occurred reading file {filepath}: {e_other}")
        return None
    
    return content


def write_file_content(filepath, content):
    """Writes content to a file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nSuccessfully wrote generated sketch to: '{OUTPUT_INO_FILE}'")
        return True
    except IOError as e:
        print(f"Error writing file {filepath}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred writing file {filepath}: {e}")
        return False

def extract_frame_data(header_content, header_filename):
    """
    Extracts just the array data block { ..., ... }; from the header content.
    Returns the block as a string, or None if extraction fails.
    """
    
    # CRITICAL FIX: Clean the content AGAIN, focusing on non-breaking spaces (chr 160)
    # and tabs which might be invisible but break regex \s
    if header_content:
        cleaned_content = header_content.replace(chr(160), ' ').replace('\t', ' ')
    else:
        return None

    # *** NEW SAFER REGEX ***
    # This regex now captures ONLY the data *inside* the braces
    #   =                  (the assignment operator)
    #   \s*\{\s* (optional whitespace, literal {, optional whitespace)
    #   (                  (start capturing group 1: the data)
    #     [\s\S]+?         (non-greedily match of any character, including newlines)
    #   )                  (end capturing group 1)
    #   \s*\};             (optional whitespace, literal }, literal ;)
    array_data_regex = re.compile(
         r"=\s*\{\s*([\s\S]+?)\s*\};",
        re.IGNORECASE | re.DOTALL
    )

    # print(f"  [DEBUG] Cleaned header snippet (first 300 chars): '{cleaned_content[:300].strip()}'")
    match = array_data_regex.search(cleaned_content) # Use the cleaned content

    if match:
        data_inside_braces = match.group(1).strip() # Capture data *inside* { };
        
        if data_inside_braces:
             # Reconstruct the block safely
             values_block = "{\n    " + data_inside_braces + "\n};"
             print(f"  [DEBUG] Regex matched. Reconstructed block.")
             return values_block
        else:
             print(f"  [DEBUG] Regex matched, but captured data block was empty. Skipping.")
             return None
    else:
        print(f"  [DEBUG] Error: Regex '={{...}};' FAILED to find a match in '{header_filename}'.")
        return None

def process_header_content(header_content, original_frame_name, header_filename_for_debug):
    """
    Extracts data, reconstructs declaration using original_frame_name and adds PROGMEM.
    Returns the full C++ definition string or None if extraction fails.
    """
    values_block = extract_frame_data(header_content, header_filename_for_debug)

    if not values_block:
        return None # Indicate failure

    # Reconstruct the full array definition WITH PROGMEM and correct name
    reconstructed_definition = (
        f"const unsigned char {original_frame_name}[] PROGMEM = {values_block};"
    )
    
    reconstructed_definition = re.sub(r';\s*;', ';', reconstructed_definition)
    
    return reconstructed_definition + "\n// Data from " + header_filename_for_debug + "\n"


# --- Main Execution ---
if __name__ == "__main__":
    print(f"Building animation sketch from template '{TEMPLATE_INO_FILE}'...")
    print(f"Looking for headers in: '{HEADER_FOLDER_NAME}'")

    if not os.path.exists(TEMPLATE_INO_PATH):
         print(f"\nError: Template file '{TEMPLATE_INO_FILE}' not found.")
         sys.exit(1)

    if not os.path.exists(HEADER_FOLDER_PATH):
        print(f"\nError: Header folder '{HEADER_FOLDER_NAME}' not found.")
        sys.exit(1)

    template_content = read_file_content(TEMPLATE_INO_FILE)
    if not template_content:
        print(f"\nCould not read the template file '{TEMPLATE_INO_FILE}'. Aborting.")
        sys.exit(1)

    if PLACEHOLDER_DEFINITIONS not in template_content or PLACEHOLDER_LOOP not in template_content:
         print(f"\nError: Placeholders '{PLACEHOLDER_DEFINITIONS}' or '{PLACEHOLDER_LOOP}' not found in the template file.")
         print("Please ensure 'templet/animation.ino' contains these exact lines as placeholders.")
         sys.exit(1)

    # Find and sort header files based on filename number
    file_pattern = os.path.join(HEADER_FOLDER_PATH, f"frame_{'[0-9]' * FRAME_NUMBER_PADDING}.h")
    found_files = glob.glob(file_pattern)

    filename_num_regex = re.compile(rf"frame_(\d{{{FRAME_NUMBER_PADDING}}})\.h", re.IGNORECASE)

    valid_frames = {}

    for fpath in found_files:
        fname = os.path.basename(fpath)
        match = filename_num_regex.match(fname)
        if match:
            frame_num = int(match.group(1))
            valid_frames[frame_num] = fpath
        else:
            print(f"  Skipping file with unexpected name format: '{fname}'")

    if not valid_frames:
        print(f"\nError: No valid header files (e.g., frame_000.h) found in '{HEADER_FOLDER_NAME}'.")
        sys.exit(1)

    sorted_frame_numbers = sorted(valid_frames.keys())
    print(f"Found and sorted {len(sorted_frame_numbers)} frame headers based on filename number.")

    all_frame_definitions = []
    loop_code_blocks = []

    for frame_num_from_filename in sorted_frame_numbers: # Iterate through 0, 1, 2...
        filepath = valid_frames[frame_num_from_filename]
        header_filename = os.path.basename(filepath)
        
        # 'frame_000.h' (number 0) becomes 'Frame1'
        # 'frame_001.h' (number 1) becomes 'Frame2'
        ino_frame_name = f"Frame{frame_num_from_filename + 1}" 

        print(f"\nProcessing {header_filename} (Assigning to {ino_frame_name})...")

        header_content = read_file_content(filepath)
        if not header_content:
            print(f"  Error: Failed to read {header_filename}. Skipping this frame.")
            continue 

        processed_definition = process_header_content(header_content, ino_frame_name, header_filename)

        if processed_definition:
            all_frame_definitions.append(processed_definition)
            
            loop_block = (
                f"  display.clearDisplay();\n"
                f"  display.drawBitmap(0, 0, {ino_frame_name}, SCREEN_WIDTH, SCREEN_HEIGHT, 1);\n"
                f"  display.display();\n"
                f"  delay(frame_delay);\n"
            )
            loop_code_blocks.append(loop_block)
            
            print(f"  Successfully processed {header_filename} as {ino_frame_name}.")
        else:
            print(f"  Error processing content of {header_filename}. Skipping this frame.")

    # Combine generated parts
    final_definitions = "\n\n".join(all_frame_definitions)
    final_loop_code = "\n".join(loop_code_blocks)

    # Replace placeholders in the template
    output_content = template_content.replace(PLACEHOLDER_DEFINITIONS, final_definitions)
    output_content = output_content.replace(PLACEHOLDER_LOOP, final_loop_code)

    # Write the final .ino file
    write_file_content(OUTPUT_INO_PATH, output_content)