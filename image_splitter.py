import os
from PIL import Image, ImageSequence

def split_gif_frames(gif_path, output_folder):
    """
    Splits frames from a GIF file, handling potential optimizations by
    compositing frames, and saves them as individual GIF files.

    Args:
        gif_path (str): Path to the input GIF file.
        output_folder (str): Path to the folder where frames will be saved.
    """
    try:
        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"Created output folder: {output_folder}")

        # Open the GIF file
        with Image.open(gif_path) as im:
            print(f"Opened GIF: {gif_path} (Mode: {im.mode})")

            # Check if the GIF is animated
            if not getattr(im, "is_animated", False):
                 print("Warning: Input file is not an animated GIF. Saving only the first frame.")
                 frame_filename = os.path.join(output_folder, "frame_000.gif")
                 im.save(frame_filename, "GIF")
                 print(f"Saved single frame to {output_folder}")
                 return

            frame_index = 0
            # Create a base frame (canvas). Use RGBA for transparency handling.
            # Use the first frame's size and mode initially, but convert to RGBA
            canvas = Image.new("RGBA", im.size)
            # Paste the first frame onto the canvas
            first_frame = im.copy().convert("RGBA")
            canvas.paste(first_frame, (0,0), first_frame) # Use alpha mask for transparency
            
            # Save the first frame
            frame_filename = os.path.join(output_folder, f"frame_{frame_index:03d}.gif")
            # Save canvas (which now holds the first full frame)
            canvas.save(frame_filename, "GIF")
            frame_index += 1

            # Store the disposal method of the *previous* frame
            # 0=No disposal, 1=Do not dispose, 2=Restore background, 3=Restore previous
            last_disposal_method = first_frame.info.get('disposal', 0)

            # Iterate through the rest of the frames
            for frame in ImageSequence.Iterator(im):
                if frame_index == 0: # Skip the first frame as we already handled it
                    frame_index += 1
                    continue

                # Get disposal method for the *current* frame (to apply *after* drawing it)
                disposal_method = frame.info.get('disposal', 0)

                # --- Handle Disposal of *Previous* Frame ---
                if last_disposal_method == 2: # Restore background
                    # Create a new transparent canvas area matching the last frame's bbox
                    # Note: A more precise implementation might use im.dispose region
                    canvas = Image.new("RGBA", im.size)
                elif last_disposal_method == 3: # Restore previous (Pillow doesn't easily support this, approximate with not disposing)
                    # For simplicity, we treat Restore Previous like Do Not Dispose (1)
                    pass # Keep the canvas as is
                # For methods 0 and 1, we also keep the canvas as is before pasting

                # --- Paste Current Frame ---
                # Convert current frame to RGBA
                frame_rgba = frame.convert("RGBA")
                # Paste the current frame onto the canvas using its alpha channel as a mask
                canvas.paste(frame_rgba, (0, 0), frame_rgba)

                # Construct the output filename
                frame_filename = os.path.join(output_folder, f"frame_{frame_index:03d}.gif")
                # Save the fully composited canvas
                canvas.save(frame_filename, "GIF")

                frame_index += 1
                last_disposal_method = disposal_method # Update for the next iteration


            print(f"Successfully extracted and composited {frame_index} frames to {output_folder} as GIF files")

    except FileNotFoundError:
        print(f"Error: GIF file not found at {gif_path}")
    except Exception as e:
        print(f"An error occurred while processing the GIF: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    import sys
    output_directory = "input_images" 

    # 1. Get the GIF path from the GUI if provided
    if len(sys.argv) > 1:
        gif_file = sys.argv[1]
    else:
        # Fallback if you run it manually without the GUI
        gif_file = "input_videos/test.gif" 

    # 2. Safety check
    if not os.path.exists(gif_file):
        print(f"Error: Could not find the file '{gif_file}'")
        sys.exit(1)

    print(f"\n--- Processing GIF: {gif_file} ---")
    
    # 3. Clear out old frames from the input_images folder before splitting a new GIF
    if os.path.exists(output_directory):
        for file in os.listdir(output_directory):
            if file.endswith(".gif"):
                os.remove(os.path.join(output_directory, file))
                
    # 4. Run the split
    split_gif_frames(gif_file, output_directory)
