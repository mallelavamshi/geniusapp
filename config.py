# Application configuration settings

# Database
DATABASE_PATH = "data/database/image_app.db"

# Directories
UPLOAD_DIR = "uploaded_images"
REPORTS_DIR = "reports"

# Image processing
MAX_IMAGE_SIZE = (800, 800)  # Maximum size for uploaded images
THUMBNAIL_SIZE = (200, 200)  # Size for thumbnails in reports
IMGBB_EXPIRATION = 600  # ImgBB image expiration in seconds

# API Settings
DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 1024

# UI Settings
PAGE_TITLE = "EstateGeniusAI"
PAGE_ICON = "🔍"
LAYOUT = "wide"

# Color Theme Settings
COLOR_THEME = {
    # Primary brand color
    "PRIMARY_COLOR": "#429FC7",
    
    # Text colors
    "HEADING_TEXT_COLOR": "#429FC7",  # Headers, titles, and headings
    "BODY_TEXT_COLOR": "#C75F42",     # Regular body text
    "LABEL_TEXT_COLOR": "#C75F42",    # Form labels and field names
    "ANALYSIS_TEXT_COLOR": "#000000", # Analysis results text (black)
    
    # Button colors
    "BUTTON_TEXT_COLOR": "#000000",   # Text color for all buttons
    "BUTTON_BORDER_COLOR": "#C75F42", # Border color for buttons
    "BUTTON_BG_COLOR": "#FFFFFF",     # Background color for buttons
    "BUTTON_HOVER_BG_COLOR": "#F5F5F5", # Background color on hover
    
    # Form and input colors
    "INPUT_BORDER_COLOR": "#E0E0E0",  # Border color for input fields
    "INPUT_BG_COLOR": "#F9F9F9",      # Background color for input fields
    
    # Status colors
    "SUCCESS_COLOR": "#4CAF50",       # Success messages and indicators
    "ERROR_COLOR": "#F44336",         # Error messages
    "WARNING_COLOR": "#FFC107",       # Warning messages
    "INFO_COLOR": "#2196F3",          # Info messages
    
    # Miscellaneous
    "BORDER_COLOR": "#E0E0E0",        # Border color for elements
    "DIVIDER_COLOR": "#E0E0E0",       # Color for dividers and separators
}

# Task Processing
MAX_RETRIES = 3  # Maximum number of retries for failed API calls
RETRY_DELAY = 5  # Delay in seconds between retries

# Claude Analysis Prompt Template
CLAUDE_PROMPT_TEMPLATE = """
Please analyze the following product matches and provide a concise summary:

{search_results}

Please identify the product, estimate its price range, and provide any other relevant information.
Keep your analysis short and to the point, focusing on the most important details.
"""

# SearchAPI Parameters
SEARCHAPI_PARAMS = {
    "engine": "google_lens",
    "search_type": "all"
}

# Excel Report Settings
EXCEL_SETTINGS = {
    "worksheet_name": "Analysis",
    "column_widths": {
        "A:A": 30,  # Image Path
        "B:B": 30,  # ImgBB URL
        "C:C": 30,  # Description
        "D:D": 50,  # Analysis
    },
    "image_column": 4,  # Column E (zero-indexed)
    "row_height": 150,
    "image_scale": 0.5
}