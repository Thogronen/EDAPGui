"""

This file loads a video file and uses OCR to look for both 0:07 and 0:05 in the center 15% of the screen. You should be aligned anyway - limiting the search area to such a small area saves a lot of time and resources!

Created by #glassesinsession
Date of creation: 9/4/2024

"""

import cv2
import numpy as np
from paddleocr import PaddleOCR

def process_frame_with_ocr(frame, ocr, x1, y1, x2, y2):
    """Apply OCR to a cropped region of a video frame and return the annotated frame."""
    cropped_frame = frame[y1:y2, x1:x2]

    result = ocr.ocr(cropped_frame)
    
    # Print OCR results to console
    for line in result:
        for item in line:
            text = item[1][0]
            confidence = item[1][1]
            print(f"Detected text: '{text}' with confidence: {confidence:.2f}")
    
    # Draw the scanned area on the original frame
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    return frame, result

def main():
    video_path = "007.mp4"  # The path to your video file
    target_text_1 = "0:07"  # The first text we are waiting to detect
    target_text_2 = "0:05"  # The second text we are waiting to detect

    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True, show_log=False)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Frames per second: {fps}")

    # Calculate how many frames correspond to half a second
    frames_to_skip = int(fps / 4)

    frame_number = 0

    # Calculate the cropping coordinates for the central 15%
    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    x1 = int(cap_width * 0.425)
    y1 = int(cap_height * 0.425)
    x2 = int(cap_width * 0.575)
    y2 = int(cap_height * 0.575)

    process_frame_number = 0  # Keep track of frames processed for OCR

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("End of video or error.")
            break

        frame_number += 1

        # Show the video smoothly (display every frame)
        cv2.imshow('Video with OCR', frame)

        # Process every half second (frames_to_skip)
        if process_frame_number % frames_to_skip == 0:
            print(f"Processing frame {frame_number}...")

            # Process the frame and get the annotated frame
            annotated_frame, ocr_result = process_frame_with_ocr(frame, ocr, x1, y1, x2, y2)
            
            # Check if "0:07" or "0:05" is found in the OCR results
            for line in ocr_result:
                for item in line:
                    text = item[1][0]
                    if target_text_1 in text:
                        print(f"Found '{target_text_1}' in frame {frame_number}.")
                        cv2.imwrite(f"debug/frame_with_{target_text_1}.png", annotated_frame)
                        print("Video paused. Press 'c' to continue or 'q' to quit.")

                        # Pause video when text is found and wait for user input
                        while True:
                            key = cv2.waitKey(0) & 0xFF
                            if key == ord('c'):
                                break  # Continue playing
                            elif key == ord('q'):
                                cap.release()
                                cv2.destroyAllWindows()
                                return  # Quit program

                    if target_text_2 in text:
                        print(f"Found '{target_text_2}' in frame {frame_number}.")
                        cv2.imwrite(f"debug/frame_with_{target_text_1}.png", annotated_frame)
                        print("Video paused. Press 'c' to continue or 'q' to quit.")

                        # Pause video when text is found and wait for user input
                        while True:
                            key = cv2.waitKey(0) & 0xFF
                            if key == ord('c'):
                                break  # Continue playing
                            elif key == ord('q'):
                                cap.release()
                                cv2.destroyAllWindows()
                                return  # Quit program
        
        # Increment the process frame counter every frame
        process_frame_number += 1

        # Check if user presses "q" to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Text not found in the video.")

if __name__ == "__main__":
    main()
