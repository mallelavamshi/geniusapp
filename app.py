import streamlit as st
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import local modules
import database as db
import processing
import ui
import utils
import config

# Replace .env loading with direct environment variable access
import os

# Get API keys from environment
api_keys = {
    'IMGBB_API_KEY': os.getenv('IMGBB_API_KEY'),
    'SEARCHAPI_API_KEY': os.getenv('SEARCHAPI_API_KEY'),
    'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app")

def apply_custom_css():
    """Apply custom CSS using the color theme from config"""
    # Import colors from config
    from config import COLOR_THEME as colors
    
    custom_css = f"""
    <style>
    /* Base text colors */
    body {{
        color: {colors["BODY_TEXT_COLOR"]};
    }}
    
    /* All headings */
    h1, h2, h3, h4, h5, h6 {{
        color: {colors["HEADING_TEXT_COLOR"]} !important;
    }}
    
    /* All paragraph text */
    p, .stMarkdown {{
        color: {colors["BODY_TEXT_COLOR"]};
    }}
    
    /* Form labels */
    label, 
    .stTextInput label, 
    .stNumberInput label,
    .stTextArea label,
    .stSelectbox label,
    .stMultiselect label {{
        color: {colors["LABEL_TEXT_COLOR"]};
    }}
    
    /* Table text color */
    [data-testid="stDataFrame"] th div p,
    [data-testid="stDataFrame"] td div p {{
        color: {colors["BODY_TEXT_COLOR"]};
    }}
    
    /* Expander headers */
    .streamlit-expanderHeader,
    button[kind="expansionpanel"] {{
        color: {colors["HEADING_TEXT_COLOR"]} !important;
    }}
    
    /* Tab text */
    .stTabs [data-baseweb="tab"] {{
        color: {colors["BODY_TEXT_COLOR"]};
    }}
    
    /* Button styling */
    button[kind="secondary"],
    .stButton > button,
    button[data-testid="baseButton-secondary"] {{
        color: {colors["BUTTON_TEXT_COLOR"]} !important;
        border-color: {colors["BUTTON_BORDER_COLOR"]} !important;
        background-color: {colors["BUTTON_BG_COLOR"]} !important;
    }}
    
    /* Button hover state */
    button[kind="secondary"]:hover,
    .stButton > button:hover,
    button[data-testid="baseButton-secondary"]:hover {{
        background-color: {colors["BUTTON_HOVER_BG_COLOR"]} !important;
    }}
    
    /* Analysis text in completed tasks */
    .analysis-results p, 
    .analysis-results li,
    .task-analysis-text,
    .stExpander .stMarkdown p, 
    [data-testid="stExpander"] .stMarkdown p,
    [data-testid="stExpander"] [data-testid="stMarkdown"] p,
    div[data-testid="stExpander"] div[data-testid="stMarkdown"] p,
    .stTabs [data-baseweb="tab-panel"] p {{
        color: {colors["ANALYSIS_TEXT_COLOR"]} !important;
    }}
    
    /* Status message colors */
    .element-container .stAlert[kind="info"] {{
        background-color: {colors["INFO_COLOR"]}22;
        border-color: {colors["INFO_COLOR"]};
        color: {colors["INFO_COLOR"]};
    }}
    
    .element-container .stAlert[kind="success"] {{
        background-color: {colors["SUCCESS_COLOR"]}22;
        border-color: {colors["SUCCESS_COLOR"]};
        color: {colors["SUCCESS_COLOR"]};
    }}
    
    .element-container .stAlert[kind="warning"] {{
        background-color: {colors["WARNING_COLOR"]}22;
        border-color: {colors["WARNING_COLOR"]};
        color: {colors["WARNING_COLOR"]};
    }}
    
    .element-container .stAlert[kind="error"] {{
        background-color: {colors["ERROR_COLOR"]}22;
        border-color: {colors["ERROR_COLOR"]};
        color: {colors["ERROR_COLOR"]};
    }}
    
    /* Form inputs styling */
    input, textarea, select, div[data-baseweb="select"] {{
        border-color: {colors["INPUT_BORDER_COLOR"]} !important;
        background-color: {colors["INPUT_BG_COLOR"]} !important;
    }}
    
    /* Add extra styling for tab content text */
    .stTabs [data-baseweb="tab-panel"] div {{
        color: {colors["ANALYSIS_TEXT_COLOR"]} !important;
    }}
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)

def apply_global_width_fixes():
    """Apply global fixes for width and centering across all pages with mobile responsiveness"""
    st.markdown("""
    <style>
    /* Universal width limit for interactive elements - responsive for mobile */
    .stTextInput, 
    .stNumberInput, 
    .stTextArea, 
    .stButton,
    .stSelectbox,
    .stMultiselect,
    .stCheckbox,
    .stRadio,
    .stDateInput,
    .stTimeInput,
    .stFileUploader {
        max-width: 100% !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    /* Desktop specific sizing */
    @media (min-width: 768px) {
        .stTextInput, 
        .stNumberInput, 
        .stTextArea, 
        .stButton,
        .stSelectbox,
        .stMultiselect,
        .stCheckbox,
        .stRadio,
        .stDateInput,
        .stTimeInput,
        .stFileUploader {
            max-width: 400px !important;
        }
    }
    
    /* Form input elements themselves */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stButton > button,
    .stSelectbox > div > div,
    .stMultiselect > div > div,
    .stFileUploader > div > input {
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* Fix button sizing */
    .stButton > button {
        width: 100% !important;
        display: inline-flex !important;
        justify-content: center !important;
    }
    
    /* Task items should scale with screen size but max 400px on desktop */
    button[kind="expansionpanel"] {
        max-width: 100% !important;
        width: 100% !important;
    }
    
    @media (min-width: 768px) {
        button[kind="expansionpanel"] {
            max-width: 400px !important;
        }
    }
    
    /* When expanded, allow full width on mobile, 800px on desktop */
    .stExpander {
        max-width: 100% !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    @media (min-width: 768px) {
        .stExpander {
            max-width: 800px !important;
        }
    }
    
    /* Camera input - improved height on mobile to take 75% of viewport height */
    .stCameraInput {
        height: 75vh !important;
        max-height: 75vh !important;
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }
    
    /* Make camera elements size properly */
    .stCameraInput > div,
    .stCameraInput [data-testid="stImage"],
    .stCameraInput [data-testid="stImage"] > div,
    .stCameraInput video {
        height: 75vh !important;
        max-height: 75vh !important;
        width: 100% !important;
        max-width: 100% !important;
        object-fit: contain !important;
    }
    
    /* Tabs - full width on mobile */
    .stTabs {
        max-width: 100% !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    @media (min-width: 768px) {
        .stTabs {
            max-width: 800px !important;
        }
    }
    
    /* Title centering */
    h1, h2, h3, .centered-title {
        text-align: center !important;
    }
    
    /* Special styling for task history view */
    .task-container {
        display: flex !important;
        align-items: center !important;
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 auto 10px auto !important;
    }
    
    @media (min-width: 768px) {
        .task-container {
            max-width: 400px !important;
        }
    }
    
    /* Trash button alignment */
    .task-container .stButton {
        margin: 0 !important;
        padding: 0 !important;
        width: auto !important;
    }
    
    /* Center main app buttons */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] {
        display: flex !important;
        justify-content: center !important;
    }
    
    /* Task creation form buttons styles */
    .task-create-form .button-container {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 auto !important;
        display: flex !important;
        gap: 10px !important;
    }
    
    @media (min-width: 768px) {
        .task-create-form .button-container {
            max-width: 400px !important;
        }
    }
    
    .task-create-form .button-col {
        flex: 1 !important;
        padding: 0 !important;
    }
    
    /* Fix for images in task analysis to fit mobile screens */
    .stExpander img, .stImage img, .stExpander [data-testid="stImage"], .stExpander [data-testid="stImage"] > div {
        max-width: 100% !important;
        height: auto !important;
        object-fit: contain !important;
    }
    
    /* Fix text overflow in task history */
    .stExpander p, 
    .stExpander div p, 
    .stExpander span,
    .analysis-results p,
    .task-analysis-text {
        max-width: 100% !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
    }
    
    /* Make results content in expanded tasks fit mobile */
    div[data-testid="stExpander"][aria-expanded="true"] [data-testid="column"] {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 100% !important;
    }
    
    @media (min-width: 768px) {
        div[data-testid="stExpander"][aria-expanded="true"] [data-testid="column"] {
            width: 390px !important;
            max-width: 390px !important;
            min-width: 390px !important;
        }
    }
    
    /* Fix for images and text in expanded content on mobile */
    @media (max-width: 767px) {
        div[data-testid="stExpander"][aria-expanded="true"] {
            width: 100% !important; 
            max-width: 100% !important;
            min-width: 100% !important;
        }
        
        div[data-testid="stExpander"][aria-expanded="true"] > div:nth-child(2) {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 100% !important;
        }
        
        /* Stack columns vertically on mobile */
        div[data-testid="stExpander"] [data-testid="column"] {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 100% !important;
        }
    }
    
    /* Fix streamlit's default horizontal scroll on mobile */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
        overflow-x: hidden !important;
    }
    
    /* Streamlit containers should be responsive */
    .element-container, [data-testid="stVerticalBlock"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    
    /* Force Streamlit's app to be full width */
    .appview-container .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        overflow-x: hidden !important;
    }
    
    /* Prevent horizontal scrolling on the entire app */
    body {
        overflow-x: hidden !important;
    }
    html {
        overflow-x: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Get API keys from environment
api_keys = {
    'IMGBB_API_KEY': os.getenv('IMGBB_API_KEY'),
    'SEARCHAPI_API_KEY': os.getenv('SEARCHAPI_API_KEY'),
    'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
}

# Application startup
def main():
    # Set page config
    st.set_page_config(
        page_title="EstateGeniusAI",
        page_icon=config.PAGE_ICON,
        layout=config.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS and width fixes
    apply_custom_css()
    apply_global_width_fixes()
    
    # Check if API keys are available
    valid, message = utils.validate_api_keys(api_keys)
    if not valid:
        st.error(f"API Key Error: {message}")
        st.error("Please check your .env file and restart the application.")
        st.stop()
    
    # Ensure required directories exist
    utils.ensure_directories()
    
    # Initialize database
    db.init_db()
    
    # Run database migrations if needed
    db.migrate_db()
    
    # Start background worker thread
    worker_thread = processing.start_worker_thread(api_keys)
    
    # Session state initialization
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'current_task_images' not in st.session_state:
        st.session_state.current_task_images = []
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    if 'file_uploader_key' not in st.session_state:
        st.session_state.file_uploader_key = 0
    if 'camera_on' not in st.session_state:
        st.session_state.camera_on = False
    if 'active_task' not in st.session_state:
        st.session_state.active_task = None
    
    # Log application start
    logger.info(f"Application started at {datetime.now()}")
    
    # Main app flow
    if st.session_state.user_id is None:
        ui.login_page()
    else:
        # Check if we should redirect to admin page
        if st.session_state.page == "admin":
            ui.admin_page()
        elif st.session_state.page == "login" or st.session_state.page == "home":
            ui.home_page()
        elif st.session_state.page == "bulk_upload":
            ui.bulk_upload_page()
        elif st.session_state.page == "single_upload":
            ui.single_upload_page()

if __name__ == "__main__":
    main()