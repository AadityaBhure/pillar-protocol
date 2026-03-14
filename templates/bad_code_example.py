"""
Bad Code Example - Incomplete Image Processing Pipeline
This code has missing implementations and unused functions.
Should fail inspection with specific feedback.
"""

from PIL import Image


class BrokenPipeline:
    def __init__(self):
        self.processed_images = []
    
    def load_image(self, filepath):
        """Load an image from file - NOT IMPLEMENTED"""
        pass  # Missing implementation
    
    def apply_grayscale(self, image):
        """Convert image to grayscale - DEFINED BUT NEVER USED"""
        return image.convert('L')
    
    def apply_blur(self, image, radius=5):
        """Apply blur - INCOMPLETE IMPLEMENTATION"""
        # Just returns the image without actually blurring
        return image
    
    # Missing resize_image function entirely
    
    def save_image(self, image, output_path):
        """Save image - NOT IMPLEMENTED"""
        pass  # Missing implementation
    
    def process_pipeline(self, input_path, output_path):
        """Incomplete pipeline"""
        # Only calls some functions, not all
        img = self.load_image(input_path)  # Returns None due to pass
        # apply_grayscale is never called
        img = self.apply_blur(img, radius=3)  # Doesn't actually blur
        # resize_image doesn't exist
        self.save_image(img, output_path)  # Doesn't actually save


# Functions are defined but not properly used
if __name__ == "__main__":
    pipeline = BrokenPipeline()
    # This will fail because implementations are missing
    pipeline.process_pipeline("input.jpg", "output.jpg")
