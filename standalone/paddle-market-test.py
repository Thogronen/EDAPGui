import cv2
import numpy as np
import os

# Configuration variables
INPUT_IMAGE = 'images/nav_panel_yellow_2048p.png'
TEMPLATE_IMAGES = {
    'top_left': 'templates/lp_top_left.png',
    'top_right': 'templates/lp_top_right.png',
    'bottom_left': 'templates/lp_bottom_left.png',
    'bottom_right': 'templates/lp_bottom_right.png',
}

def template_matching(image, template, method=cv2.TM_CCOEFF_NORMED):
    if len(image.shape) == 3:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_gray = image

    if len(template.shape) == 3:
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    else:
        template_gray = template

    res = cv2.matchTemplate(image_gray, template_gray, method)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    
    # Calculate the center of the matched area
    center_x = max_loc[0] + template_gray.shape[1] // 2
    center_y = max_loc[1] + template_gray.shape[0] // 2
    
    return (center_x, center_y), max_val

def find_corners_with_templates(image, templates):
    corners = {}
    for name, template in templates.items():
        center, confidence = template_matching(image, template)
        print(f"Template '{name}' matched with confidence: {confidence:.2f}")
        corners[name] = center
    
    return corners

def correct_perspective(image, corners):
    if len(corners) != 4:
        print("Error: Not all corners were detected.")
        return image

    src_pts = np.array([corners['top_left'], corners['top_right'], 
                        corners['bottom_right'], corners['bottom_left']], dtype=np.float32)

    # Calculate the desired width and height
    width = max(np.linalg.norm(np.array(corners['top_right']) - np.array(corners['top_left'])),
                np.linalg.norm(np.array(corners['bottom_right']) - np.array(corners['bottom_left'])))
    height = max(np.linalg.norm(np.array(corners['bottom_left']) - np.array(corners['top_left'])),
                 np.linalg.norm(np.array(corners['bottom_right']) - np.array(corners['top_right'])))

    # Add some padding
    padding = 50
    width += padding * 2
    height += padding * 2

    dst_pts = np.array([[padding, padding], [width - padding, padding], 
                        [width - padding, height - padding], [padding, height - padding]], dtype=np.float32)

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    corrected = cv2.warpPerspective(image, M, (int(width), int(height)))

    print(f"Perspective correction applied. New dimensions: {width:.0f}x{height:.0f}")
    return corrected

def save_debug_image(image, filename):
    debug_dir = 'debug'
    os.makedirs(debug_dir, exist_ok=True)
    filepath = os.path.join(debug_dir, filename + '.png')
    cv2.imwrite(filepath, image)
    print(f"Saved image: {filepath}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, INPUT_IMAGE)
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return
    
    original_image = cv2.imread(image_path)
    
    if original_image is None:
        print(f"Error: Could not read image at {image_path}")
        return

    # Load templates
    templates = {}
    for name, path in TEMPLATE_IMAGES.items():
        template_path = os.path.join(script_dir, path)
        template = cv2.imread(template_path)
        if template is None:
            print(f"Error: Could not read template image at {template_path}")
            return
        templates[name] = template

    # Find corners using templates
    corners = find_corners_with_templates(original_image, templates)

    # Draw detected corners on the original image for debugging
    debug_image = original_image.copy()
    for name, corner in corners.items():
        cv2.circle(debug_image, corner, 5, (0, 255, 0), -1)
        cv2.putText(debug_image, name, (corner[0] + 5, corner[1] + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    save_debug_image(debug_image, 'detected_corners')

    # Apply perspective correction
    corrected_image = correct_perspective(original_image, corners)
    
    # Save the warped image
    save_debug_image(corrected_image, 'perspective_corrected_image')
    
    print("Processing complete. Check the DEBUG folder for the detected corners and perspective-corrected image.")

if __name__ == "__main__":
    main()