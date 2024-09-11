"""

This file allows you to make templates based on a set image. Run the script, pick a name for your file, and select the area you want to be your template. The new template image will be created in the templates folder!

Created by #glassesinsession
Date of creation: 9/4/2024

"""

import cv2
import numpy as np
import os
import logging
import colorlog

# Set up the logger with colorlog
def setup_logger():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s:%(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    ))
    
    logger = logging.getLogger('template_logger')
    logger.setLevel(logging.DEBUG)  # Adjust the logging level here (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.addHandler(handler)
    return logger

logger = setup_logger()

def capture_template(image, save_path, template_name):
    """Capture a region of the image manually and save it as a template."""
    roi = cv2.selectROI("Select Template", image)
    template = image[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]
    
    template_path = os.path.join(save_path, f"{template_name}.png")
    cv2.imwrite(template_path, template)
    
    logger.info(f"Template saved: {template_path}")
    cv2.destroyWindow("Select Template")
    return template

def create_templates_from_image(image_path, save_path):
    """Create multiple templates from the provided image."""
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_image_path = os.path.join(script_dir, image_path)
    
    # image = cv2.imread(full_image_path, cv2.IMREAD_GRAYSCALE) # Can convert the image to grayscale if needed - might be nice for UI's with different color schemes.
    image = cv2.imread(full_image_path)
    if image is None:
        logger.error(f"Error: Could not load image from {full_image_path}")
        return

    logger.info(f"Loaded image from: {full_image_path}")
    
    while True:
        template_name = input("Enter a name for the new template (or 'q' to quit): ")
        if template_name.lower() == 'q':
            logger.debug("Exiting template creation...")
            break

        # Capture and save the template
        capture_template(image, save_path, template_name)

def main():
    image_path = "nav_panel_pink.png"  # Path to the image you want to take the template images from
    save_path = "templates"  # Path to the folder where templates will be saved
    
    create_templates_from_image(image_path, save_path)

if __name__ == "__main__":
    main()
