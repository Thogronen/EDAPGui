"""

This file uses template images to narrow down a screen, after which it will do OCR the set ROI. 
Right now, I'm using the market screen to check the commodity list and amounts in hold. You can change the image and tempate images as you wish!

Created by #glassesinsession
Date of creation: 9/4/2024

"""

import cv2
import numpy as np
import os
from paddleocr import PaddleOCR
import time
import paddle

def check_gpu_version():
    return paddle.device.is_compiled_with_cuda()

def calculate_scaling_factors(image_shape, reference_shape=(1920, 1080)):
    """Calculate scaling factors based on the image resolution and a reference resolution."""
    scale_x = image_shape[1] / reference_shape[0]  # Scaling factor for width
    scale_y = image_shape[0] / reference_shape[1]  # Scaling factor for height
    return scale_x, scale_y

def template_matching(image, template, method=cv2.TM_CCOEFF_NORMED):
       if len(image.shape) == 3:
           image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
       else:
           image_gray = image

       if len(template.shape) == 3:
           template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
       else:
           template_gray = template

       best_confidence = -1
       best_result = None

       for scale in [1.0, 0.75, 0.5]:  # Reduced number of scales
           if scale != 1.0:
               scaled_image = cv2.resize(image_gray, None, fx=scale, fy=scale)
           else:
               scaled_image = image_gray
           
           w, h = template_gray.shape[::-1]
           res = cv2.matchTemplate(scaled_image, template_gray, method)
           _, max_val, _, max_loc = cv2.minMaxLoc(res)

           if max_val > best_confidence:
               best_confidence = max_val
               best_result = (
                   (int(max_loc[0]/scale), int(max_loc[1]/scale)),
                   (int((max_loc[0] + w)/scale), int((max_loc[1] + h)/scale)),
                   max_val
               )

       return best_result if best_result else ((0, 0), (0, 0), 0)
def check_templates(image, templates, threshold=0.7):
    """Check if all templates are found with sufficient confidence."""
    found_templates = {}
    for name, template in templates.items():
        top_left, bottom_right, confidence = template_matching(image, template)
        print(f"Template '{name}' confidence: {confidence:.2f}")
        if confidence >= threshold:
            found_templates[name] = (top_left, bottom_right, confidence)
    return found_templates

def save_debug_image(image, filename):
    """Save an image to the debug folder."""
    debug_dir = 'debug'
    os.makedirs(debug_dir, exist_ok=True)
    filepath = os.path.join(debug_dir, filename + '.png')
    cv2.imwrite(filepath, image)
    print(f"Saved image: {filepath}")

def draw_template_match(image, top_left, bottom_right, confidence, name):
    """Draw bounding box around the found template."""
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    cv2.putText(image, f'{name}: {confidence:.2f}', (top_left[0], top_left[1] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

def define_market_area(image, debug=False, crop_top=0, crop_bottom=0, crop_left=0, crop_right=0): # Replace these with your own template names!
    """Define the area of the market based on template matching, with manual cropping."""
    templates = {
        'market_top': cv2.imread('templates/market_top.png', cv2.IMREAD_GRAYSCALE),
        'market_left': cv2.imread('templates/market_left.png', cv2.IMREAD_GRAYSCALE),
        'market_right': cv2.imread('templates/market_right.png', cv2.IMREAD_GRAYSCALE),
        'market_bottom': cv2.imread('templates/market_bottom.png', cv2.IMREAD_GRAYSCALE),
    }

    found_templates = check_templates(image, templates)

    if found_templates:
        roi_top, roi_left = 0, 0
        roi_bottom, roi_right = image.shape[0], image.shape[1]

        for name, (top_left, bottom_right, _) in found_templates.items():
            if name == 'market_top':
                roi_top = max(roi_top, bottom_right[1])
            elif name == 'market_left':
                roi_left = max(roi_left, bottom_right[0])
            elif name == 'market_right':
                roi_right = min(roi_right, top_left[0])
            elif name == 'market_bottom':
                roi_bottom = min(roi_bottom, top_left[1])

        # Apply manual cropping
        height, width = roi_bottom - roi_top, roi_right - roi_left
        roi_top += int(height * crop_top / 100)
        roi_bottom -= int(height * crop_bottom / 100)
        roi_left += int(width * crop_left / 100)
        roi_right -= int(width * crop_right / 100)

        roi = image[roi_top:roi_bottom, roi_left:roi_right]
        
        return roi, (roi_top, roi_left, roi_bottom, roi_right)
    else:
        print("Could not find any templates. Using full image.")
        return image, (0, 0, image.shape[0], image.shape[1])

def process_area_with_ocr(image, area_function, ocr, area_name="", debug=False):
    roi, roi_coords = area_function(image)
    if roi is None:
        print("ROI is invalid or templates not found. Skipping OCR.")
        return None

    ocr_result = ocr.ocr(roi)
    
    if debug:
        debug_image = image.copy()
        roi_top, roi_left, roi_bottom, roi_right = roi_coords
        cv2.rectangle(debug_image, (roi_left, roi_top), (roi_right, roi_bottom), (0, 0, 255), 2)

        for line in ocr_result:
            for item in line:
                if isinstance(item, list) and len(item) == 2:
                    points, (text, confidence) = item
                elif isinstance(item, dict):
                    points = item['box']
                    text = item['text']
                    confidence = item['confidence']
                else:
                    continue

                points = np.array(points).astype(np.int32)
                points[:, 0] += roi_left
                points[:, 1] += roi_top
                cv2.polylines(debug_image, [points], True, (0, 255, 0), 2)
                cv2.putText(debug_image, f"{text} ({confidence:.2f})", 
                            (points[0][0], points[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        save_debug_image(debug_image, f'{area_name}_ocr')

    return ocr_result

def apply_ocr_to_roi(roi, ocr, debug=False, area_name=""):
    """Apply OCR to the region of interest and annotate the image."""
    result = ocr.ocr(roi)
    if debug:
        for line in result:
            if isinstance(line, list) and len(line) == 2:
                position, (text, confidence) = line
            elif isinstance(line, dict):
                position = line['box']
                text = line['text']
                confidence = line['confidence']
            else:
                print(f"Unexpected result structure: {line}")
                continue

            if isinstance(position[0], list):
                top_left = tuple(map(int, position[0]))
                bottom_right = tuple(map(int, position[2]))
            else:
                top_left = tuple(map(int, position[:2]))
                bottom_right = tuple(map(int, position[2:]))

            cv2.rectangle(roi, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(roi, f'{text} ({confidence:.2f})', 
                        (top_left[0], top_left[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        save_debug_image(roi, f'{area_name}_ocr')
    return result



def main():
    start_time = time.time()  # Start the timer
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, 'market_full_1080p.png') # Your image of choice
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return
    
    gpu_available = check_gpu_version() # Checks if you have CUDA installed, too (?) 
    print(f"GPU version of PaddlePaddle installed: {gpu_available}")

    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False) # There is no need to use the GPU, bu you can set it to True if you want to :)
    original_image = cv2.imread(image_path)

    def market_area_with_crop(image): ## Market area
        return define_market_area(image, crop_top=0, crop_bottom=0, crop_left=10, crop_right=40) # Change the ROI crop if the area is too small/large and it interferes with your desired area to read. We go from 0 to 100, taking away from the side you pick. 10 = 10%, etc.

    processed_market_area = process_area_with_ocr(original_image, market_area_with_crop, ocr, area_name="market_area", debug=True)

    print("OCR Results:")
    if processed_market_area is not None:  # Added this check to prevent the "None" object warning when no readable objects are found
        for line in processed_market_area:
            for item in line:
                if isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[1], (list, tuple)):
                    text, confidence = item[1]
                elif isinstance(item, dict):
                    text, confidence = item['text'], item['confidence']
                else:
                    continue
                print(f"Text: {text}, Confidence: {confidence:.2f}")
    else:
        print("No OCR results to display.")

    end_time = time.time()  # Stop the timer
    execution_time = end_time - start_time  # Calculate the execution time

    print(f"Processing complete. Total execution time: {execution_time:.2f} seconds")
    print("Check the DEBUG folder for the market area image with OCR results.")

if __name__ == "__main__":
    main()