"""
Icon converter script for Decksmith
Converts PNG to ICO format for use with PyInstaller
"""

import os
import sys

def convert_to_ico():
    """Convert the icon image to ICO format"""
    try:
        from PIL import Image
        
        # Paths
        png_path = "assets/decksmith_icon.png"
        ico_path = "assets/decksmith_icon.ico"
        
        if not os.path.exists(png_path):
            print(f"❌ Please save the icon image as: {png_path}")
            return False
            
        # Open and convert
        with Image.open(png_path) as img:
            # Resize to common icon sizes and save as ICO
            icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
            img.save(ico_path, format='ICO', sizes=icon_sizes)
            
        print(f"✅ Icon converted successfully: {ico_path}")
        return True
        
    except ImportError:
        print("❌ Pillow library not found. Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Error converting icon: {e}")
        return False

if __name__ == "__main__":
    convert_to_ico()
