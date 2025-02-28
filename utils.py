import os
import io
import base64
from PIL import Image
import json

def ensure_directories():
    """Ensure all required directories exist"""
    directories = ["uploaded_images", "reports"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Add these functions to utils.py

def get_styled_text(text, color_key="BODY_TEXT_COLOR", element_type="span", additional_styles=""):
    """
    Create styled HTML text using the color theme
    
    Args:
        text (str): The text content to style
        color_key (str): The key in COLOR_THEME to use for text color
        element_type (str): HTML element type (span, p, h1, etc.)
        additional_styles (str): Any additional inline styles
        
    Returns:
        str: HTML string with styled text
    """
    from config import COLOR_THEME as colors
    color = colors.get(color_key, colors["BODY_TEXT_COLOR"])
    
    return f'<{element_type} style="color: {color}; {additional_styles}">{text}</{element_type}>'

def apply_theme_colors(html_content, replacements):
    """
    Replace color placeholders in HTML with actual theme colors
    
    Args:
        html_content (str): HTML content with {{COLOR_KEY}} placeholders
        replacements (dict): Additional replacements beyond color theme
        
    Returns:
        str: HTML with colors replaced
    """
    from config import COLOR_THEME as colors
    
    # First replace color theme keys
    for key, value in colors.items():
        placeholder = f"{{{{{key}}}}}"
        html_content = html_content.replace(placeholder, value)
    
    # Then apply any additional replacements
    for key, value in replacements.items():
        placeholder = f"{{{{{key}}}}}"
        html_content = html_content.replace(placeholder, value)
    
    return html_content

def get_file_extension(filename):
    """Get the file extension from a filename"""
    return os.path.splitext(filename)[1].lower()

def is_valid_image(file_extension):
    """Check if the file extension is a valid image format"""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    return file_extension in valid_extensions

def image_to_base64(image_path):
    """Convert an image file to base64 encoding"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"Error encoding image: {str(e)}")
        return None

def base64_to_image(base64_string, output_path):
    """Convert a base64 string to an image file"""
    try:
        image_data = base64.b64decode(base64_string)
        with open(output_path, "wb") as image_file:
            image_file.write(image_data)
        return True
    except Exception as e:
        print(f"Error decoding image: {str(e)}")
        return False

def resize_image_file(input_path, output_path, max_size=(800, 800)):
    """Resize an image file while maintaining aspect ratio"""
    try:
        image = Image.open(input_path)
        image.thumbnail(max_size)
        image.save(output_path)
        return True
    except Exception as e:
        print(f"Error resizing image: {str(e)}")
        return False

def pretty_print_json(json_data):
    """Convert JSON data to a pretty-printed string"""
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError:
            return json_data
    
    return json.dumps(json_data, indent=2)

def format_file_size(size_bytes):
    """Format file size from bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024 or unit == 'GB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024

def get_mime_type(file_extension):
    """Get MIME type from file extension"""
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.pdf': 'application/pdf',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.csv': 'text/csv',
        '.txt': 'text/plain',
        '.html': 'text/html',
        '.json': 'application/json',
    }
    return mime_types.get(file_extension.lower(), 'application/octet-stream')

def validate_api_keys(api_keys):
    """Validate API keys are properly set"""
    for key, value in api_keys.items():
        if not value or value == 'your_api_key_here':
            return False, f"Missing or invalid API key: {key}"
    return True, "All API keys are valid"