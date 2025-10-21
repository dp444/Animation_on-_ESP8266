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
    output_directory = "input_images" # Unified output folder name

    # --- GIF Example ---
    gif_file = "input_videos/test.gif"  # Replace with your GIF file path

    # Create a dummy GIF if it doesn't exist for testing
    if not os.path.exists(gif_file):
        print(f"\nNote: Creating a dummy optimized GIF '{gif_file}' for demonstration.")
        # Frame 1: Red background
        frame1 = Image.new('RGB', (60, 40), color = 'red')
        # Frame 2: Blue rectangle overlaying part of Frame 1
        frame2_overlay = Image.new('RGB', (30, 20), color = 'blue')
        frame2 = frame1.copy()
        frame2.paste(frame2_overlay, (15, 10)) # Paste blue box in the middle
        # Frame 3: Green circle overlaying part of Frame 2
        frame3_overlay = Image.new('RGBA', (20, 20), color=(0,0,0,0)) # Transparent circle base
        draw = ImageDraw.Draw(frame3_overlay)
        draw.ellipse((0, 0, 19, 19), fill='green')
        frame3 = frame2.copy()
        frame3.paste(frame3_overlay, (35, 15), frame3_overlay) # Paste green circle offset

        # Save as an optimized GIF (Pillow might not optimize aggressively, but demonstrates structure)
        frame1.save(gif_file, save_all=True, append_images=[frame2, frame3], duration=200, loop=0, optimize=True, disposal=2) # Use disposal=2
        print(f"Dummy optimized GIF '{gif_file}' created.")


    print("\n--- Processing GIF ---")
    split_gif_frames(gif_file, output_directory) # Use unified output directory

    print("\n--- Video processing skipped as only GIF input is used. ---")