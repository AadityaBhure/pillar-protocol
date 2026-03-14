"""
Good Code Example - Image Processing Pipeline
This code demonstrates a complete implementation with all functions defined AND used.
Should pass inspection with 100% coverage.
"""

from PIL import Image
import os


class ImagePipeline:
    def __init__(self):
        self.processed_images = []
    
    def load_image(self, filepath):
        """Load an image from file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Image not found: {filepath}")
        return Image.open(filepath)
    
    def apply_grayscale(self, image):
        """Convert image to grayscale"""
        return image.convert('L')
    
    def apply_blur(self, image, radius=5):
        """Apply blur filter to image"""
        from PIL import ImageFilter
        return image.filter(ImageFilter.GaussianBlur(radius))
    
    def resize_image(self, image, width, height):
        """Resize image to specified dimensions"""
        return image.resize((width, height))
    
    def save_image(self, image, output_path):
        """Save processed image to file"""
        image.save(output_path)
        self.processed_images.append(output_path)
    
    def process_pipeline(self, input_path, output_path):
        """Complete processing pipeline - loads, processes, and saves"""
        # Load image
        img = self.load_image(input_path)
        
        # Apply grayscale
        img = self.apply_grayscale(img)
        
        # Apply blur
        img = self.apply_blur(img, radius=3)
        
        # Resize
        img = self.resize_image(img, 800, 600)
        
        # Save
        self.save_image(img, output_path)
        
        return output_path


# IMPORTANT: Functions are actually used here
if __name__ == "__main__":
    pipeline = ImagePipeline()
    
    # Example usage - all functions are called
    try:
        result = pipeline.process_pipeline("input.jpg", "output.jpg")
        print(f"Image processed successfully: {result}")
        print(f"Total processed images: {len(pipeline.processed_images)}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Note: This is a demo. Create 'input.jpg' to test.")
