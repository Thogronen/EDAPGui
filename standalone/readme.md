# OCR Template Creation and Image Processing

## Overview
This project provides a set of Python scripts for working with image processing and template matching using OpenCV, PaddleOCR, and other related libraries. The scripts are designed to allow users to extract text from local images and videos, create custom templates from specific regions of images, and perform various OCR tasks.

**Important:** These scripts do **NOT** work with live games. They are built to work with **local images** and **videos** only.

## Project Structure

- `paddle-test.py`: 
  - Main OCR processing script that allows you to apply OCR to specific areas of an image based on template matching.
  - Includes various pre-processing steps such as skew correction and cropping.
  
- `manual_templates.py`: 
  - Script for creating custom templates by selecting regions of interest (ROI) from images.
  - Prompts you to select parts of an image to use as templates and saves them for later use.

- `read_image_only.py`: 
  - A simplified script that processes a static image, applies OCR, and outputs the results directly onto the image itself.
  
- `paddle-debug.py`: 
  - A debugging version of the main OCR script, including detailed log outputs and additional debug images for inspection. You should not need this, but if you do... it's here.
  
- `007.py`: 
  - A video-processing script that applies OCR to specific frames of a video, checking for text like timestamps and other relevant information.

## How-to-use

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Thogronen/EDAPGui.git
   
2. **Create a Virtual Environment:**  (Optional)
    You can either create one yourself, or run auto_vEnv.py. This ensures there's no conflict between the requirements and your exisiting installation. If you happen to close the console - no worries. Simply run open_console.bat and get right back into your VE.

3. **Install the requirements:** 
    ```bash 
    pip install -r requirements.txt

4. **Run the files:** 
  
  Run any of the python files via
    ```bash 
    python filename.py

  Feel free to change the files you run with the scripts!