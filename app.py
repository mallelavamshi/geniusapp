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
    """Apply global fixes for width and centering across all pages"""
    st.markdown("""
    <style>
    /* Universal width limit for interactive elements */
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
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    /* Form input elements themselves */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stButton > button,
    .stSelectbox > div > div,
    .stMultiselect > div > div,
    .stFileUploader > div > input {
        max-width: 400px !important;
        width: 100% !important;
    }
    
    /* Fix button sizing */
    .stButton > button {
        width: 100% !important;
        display: inline-flex !important;
        justify-content: center !important;
    }
    
    /* Task items should be 400px but expanded content can be 800px */
    button[kind="expansionpanel"] {
        max-width: 400px !important;
    }
    
    /* When expanded, allow 800px width */
    .stExpander {
        max-width: 800px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    /* Camera input */
    .stCameraInput > div {
        max-width: 400px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    /* Tabs */
    .stTabs {
        max-width: 800px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    /* Title centering */
    h1, h2, h3, .centered-title {
        text-align: center !important;
    }
    
    /* Special styling for task history view */
    .task-container {
        display: flex !important;
        align-items: center !important;
        max-width: 400px !important;
        margin: 0 auto 10px auto !important;
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
        max-width: 400px !important;
        margin: 0 auto !important;
        display: flex !important;
        gap: 10px !important;
    }
    
    .task-create-form .button-col {
        flex: 1 !important;
        padding: 0 !important;
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