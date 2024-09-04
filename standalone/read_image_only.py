import cv2
import numpy as np
from paddleocr import PaddleOCR
import os

def apply_ocr_and_annotate(image, ocr, output_path, debug=False):
    """Apply OCR to the image and annotate the image with the recognized text."""
    
    # Apply OCR on the image
    result = ocr.ocr(image)
    
    # If the image is grayscale, convert it to BGR for annotation
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    # Annotate the image with the OCR results
    for res in result:
        for line in res:
            points = np.array(line[0]).astype(np.int32)
            cv2.polylines(image, [points.reshape(-1, 1, 2)], True, (0, 255, 0), 2)
            text_position = (points[0][0], points[0][1] - 10)
            cv2.putText(image, f"{line[1][0]} ({line[1][1]:.2f})", text_position,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Save the annotated image
    cv2.imwrite(output_path, image)
    print(f"OCR output saved to: {output_path}")
    
    if debug:
        cv2.imshow('OCR Result', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    # Specify the image path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, 'nav_panel.png')  # Replace with your image filename
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    # Initialize OCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)

    # Load the image
    image = cv2.imread(image_path)

    # Define the output path
    output_path = os.path.join(script_dir, 'debug/ocr_output.png')

    # Apply OCR and annotate the image
    apply_ocr_and_annotate(image, ocr, output_path, debug=True)

if __name__ == "__main__":
    main()
