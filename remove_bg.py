#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *
import os
import subprocess

# Path to your Python 3 interpreter and script - (C:/USERS/....)
PYTHON3 = r"LOCATION OF PYTHON ON COMPUTER"
SCRIPT  = r"LOCATION OF remove_bg_bridge.py on COMPUTER"

def remove_bg(image, drawable):
    pdb.gimp_image_undo_group_start(image)
    try:
        # Temporary input/output files
        temp_in = os.path.join(os.environ["TEMP"], "gimp_input.png")
        temp_out = os.path.join(os.environ["TEMP"], "gimp_output.png")

        # Export current layer
        pdb.file_png_save_defaults(image, drawable, temp_in, temp_in)

        # Run external Python 3 script
        cmd = [PYTHON3, SCRIPT, temp_in, temp_out]
        subprocess.call(cmd)

        # Load result into GIMP as new layer
        if os.path.exists(temp_out):
            new_layer = pdb.gimp_file_load_layer(image, temp_out)
            image.add_layer(new_layer, 0)

            # Delete the original layer
            image.remove_layer(drawable)

            pdb.gimp_message("Background removed: original layer deleted, new transparent layer added.")
        else:
            pdb.gimp_message("Bridge script failed: no output file created.")

    except Exception as e:
        pdb.gimp_message("Error: " + str(e))

    finally:
        pdb.gimp_image_undo_group_end(image)


register(
    "python_fu_remove_bg",
    "Remove background with Python 3 bridge",
    "Runs external Python 3 OpenCV script to remove background",
    "Arushan", "Arulraj", "2025",
    "<Image>/Remove Background",
    "*",
    [],
    [],
    remove_bg
)

main()
