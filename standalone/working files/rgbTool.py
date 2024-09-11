import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from matplotlib import pyplot as plt
from tkinter import ttk


class RGBMatrixAdjuster:
    def __init__(self):
        # Initialize window and parameters
        self.root = tk.Tk()
        self.root.title("Elite Dangerous HUD Editor")
        
        self.image = None  # The loaded image
        self.panel = None
        
        # Color transformation matrix (default identity matrix)
        self.matrix = np.array([[1.0, 0.0, 0.0],  # R -> R
                                [0.0, 1.0, 0.0],  # G -> G
                                [0.0, 0.0, 1.0]]) # B -> B
        
        # Dictionary to store sliders for easy access
        self.sliders = {}
        
        self.initUI()
        
    def initUI(self):
        # UI for importing and loading the image
        load_button = tk.Button(self.root, text="Load HUD Image", command=self.load_image)
        load_button.grid(row=0, column=0, columnspan=6)
        
        # Sliders for adjusting the matrix
        self.create_slider("R->R", 1.0, 0, 1)
        self.create_slider("R->G", 0.0, 0, 2)
        self.create_slider("R->B", 0.0, 0, 3)
        
        self.create_slider("G->R", 0.0, 1, 1)
        self.create_slider("G->G", 1.0, 1, 2)
        self.create_slider("G->B", 0.0, 1, 3)
        
        self.create_slider("B->R", 0.0, 2, 1)
        self.create_slider("B->G", 0.0, 2, 2)
        self.create_slider("B->B", 1.0, 2, 3)
        
        # Export and Import buttons
        export_btn = tk.Button(self.root, text="Export to XML", command=self.export_matrix_to_xml)
        export_btn.grid(row=5, column=0, columnspan=3)
        
        import_btn = tk.Button(self.root, text="Import XML", command=self.import_matrix_from_xml)
        import_btn.grid(row=5, column=3, columnspan=3)
        
        self.root.mainloop()
        
    def create_slider(self, label, default, row, col):
        # Create a label and slider for matrix adjustments
        lbl = tk.Label(self.root, text=label)
        lbl.grid(row=row+1, column=col)
        
        slider = ttk.Scale(self.root, from_=0.0, to_=1.0, value=default, command=self.update_matrix)
        slider.set(default)
        slider.grid(row=row+1, column=col+1)
        entry = tk.Entry(self.root, width=5)
        entry.insert(0, str(default))
        entry.grid(row=row+1, column=col+2)
        
        # Store the slider in a dictionary for easy access
        self.sliders[label] = slider
        
        slider.bind("<B1-Motion>", lambda event, e=entry, s=slider: self.update_entry(e, s))
        entry.bind("<Return>", lambda event, s=slider, e=entry: self.update_slider(s, e))
        
    def update_entry(self, entry, slider):
        # Update text entry based on slider
        entry.delete(0, tk.END)
        entry.insert(0, f"{slider.get():.2f}")
        
    def update_slider(self, slider, entry):
        # Update slider based on text entry
        try:
            val = float(entry.get())
            slider.set(val)
        except ValueError:
            pass

    def update_matrix(self, *args):
        # Updates the transformation matrix based on slider values
        # Fetch values directly from sliders
        self.matrix[0, 0] = self.sliders["R->R"].get()
        self.matrix[0, 1] = self.sliders["R->G"].get()
        self.matrix[0, 2] = self.sliders["R->B"].get()
        
        self.matrix[1, 0] = self.sliders["G->R"].get()
        self.matrix[1, 1] = self.sliders["G->G"].get()
        self.matrix[1, 2] = self.sliders["G->B"].get()
        
        self.matrix[2, 0] = self.sliders["B->R"].get()
        self.matrix[2, 1] = self.sliders["B->G"].get()
        self.matrix[2, 2] = self.sliders["B->B"].get()
        
        if self.image is not None:
            self.apply_transformation()
    
    def apply_transformation(self):
        # Apply color transformation to the loaded image
        transformed_image = self.process_image(self.image, self.matrix)
        self.show_image(transformed_image)
        
    def load_image(self):
        # Load an image from disk
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = cv2.imread(file_path)
            self.show_image(self.image)
            
    def show_image(self, image):
        # Show image in the panel
        cv2.imshow('Transformed Image', image)
    
    def process_image(self, image, matrix):
        # 1. Linearize the image (gamma correction)
        linear_image = self.linearize_image(image)
        
        # 2. Apply color matrix transformation
        transformed_image = self.apply_color_matrix(linear_image, matrix)
        
        # 3. Convert back to sRGB (delinearize)
        final_image = self.delinearize_image(transformed_image)
        
        return final_image.astype(np.uint8)

    def linearize_image(self, image):
        # Convert sRGB to linear RGB using gamma correction
        return np.power(image / 255.0, 2.2)

    def delinearize_image(self, image):
        # Convert linear RGB back to sRGB using reverse gamma correction
        return np.power(image, 1 / 2.2) * 255.0

    def apply_color_matrix(self, image, matrix):
        # Apply the color transformation matrix on the linearized image
        reshaped_image = image.reshape(-1, 3)
        transformed_image = reshaped_image @ matrix.T
        return transformed_image.reshape(image.shape)
    
    def export_matrix_to_xml(self):
        # Export transformation matrix to XML format
        matrix_xml = f"""
        <Matrix>
        <Row>{self.matrix[0, 0]:.3f}, {self.matrix[0, 1]:.3f}, {self.matrix[0, 2]:.3f}</Row>
        <Row>{self.matrix[1, 0]:.3f}, {self.matrix[1, 1]:.3f}, {self.matrix[1, 2]:.3f}</Row>
        <Row>{self.matrix[2, 0]:.3f}, {self.matrix[2, 1]:.3f}, {self.matrix[2, 2]:.3f}</Row>
        </Matrix>
        """
        with open("color_matrix.xml", "w") as file:
            file.write(matrix_xml)
        print("Matrix exported to color_matrix.xml")
    
    def import_matrix_from_xml(self):
        # Import transformation matrix from XML format (not implemented yet)
        pass


if __name__ == "__main__":
    ex = RGBMatrixAdjuster()
