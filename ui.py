import streamlit as st
from PIL import Image
import os
import time
import io
import sqlite3
import pandas as pd

# Import local modules
import database as db
import processing
import config

def login_page():
    """Render the login/registration page with proper width and centering"""
    # Apply custom CSS for login page
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px !important;
        margin: 0 auto;
        padding: 20px;
        text-align: center;
    }
    .login-logo {
        margin-bottom: 20px;
        display: flex;
        justify-content: center;
    }
    .login-logo img {
        max-width: 200px;
    }
    /* Force tab width */
    .stTabs {
        max-width: 400px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    /* Force tab content width */
    .stTabs [data-baseweb="tab-list"] {
        width: 400px !important;
        max-width: 400px !important;
    }
    /* Hide the default Streamlit header */
    header {
        visibility: hidden;
    }
    /* Make the login container more centered vertically */
    .main .block-container {
        padding-top: -4rem;
    }
    /* Force buttons to be centered */
    .stButton {
        display: flex;
        justify-content: center;
    }
    .stButton > button {
        max-width: 400px !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a centered container for login
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Display centered logo only (no title)
    st.markdown('<div class="login-logo"><img src="https://i.ibb.co/5jVRLxC/logo-placeholder.png" alt="EstateGeniusAI Logo"></div>', unsafe_allow_html=True)
    
    # Create tabs for login/register
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        st.subheader("Sign In")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        login_button = st.button("Login", use_container_width=True)
        
        if login_button:
            user_id = db.authenticate_user(login_username, login_password)
            if user_id:
                st.session_state.user_id = user_id
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Sign Up")
        st.info("New user registration is currently disabled. Please contact: clara@estategeniusai.com")
        
        # Disabled form fields
        st.text_input("Username", key="reg_username", disabled=True)
        st.text_input("Password", type="password", key="reg_password", disabled=True)
        st.text_input("Confirm Password", type="password", disabled=True)
        st.button("Register", use_container_width=True, disabled=True)
    
    # Close the login container div
    st.markdown('</div>', unsafe_allow_html=True)

def home_page():
    """Render the home page with task selection and user information in header"""
    # Display user information in the header
    display_user_header()
    
    # Get username for welcome message
    user_info = db.get_user_info(st.session_state.user_id)
    username = user_info["username"] if user_info else f"User #{st.session_state.user_id}"
    
    # More aggressive CSS to force width of expanded content and make responsive
    st.markdown("""
    <style>
    /* Basic centered content */
    .centered-content {
        max-width: 100%;
        margin: 0 auto;
        text-align: center;
    }
    
    @media (min-width: 768px) {
        .centered-content {
            max-width: 400px;
        }
    }
    
    .centered-title {
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Make task buttons responsive */
    div[data-testid="stExpander"] {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }
    
    @media (min-width: 768px) {
        div[data-testid="stExpander"] {
            width: 400px !important;
            max-width: 400px !important;
        }
    }
    
    /* Force expanded content to be full width on mobile, 800px on desktop */
    div[data-testid="stExpander"][aria-expanded="true"] {
        width: 100% !important; 
        max-width: 100% !important;
    }
    
    @media (min-width: 768px) {
        div[data-testid="stExpander"][aria-expanded="true"] {
            width: 800px !important; 
            max-width: 800px !important;
        }
    }
    
    /* Crucial fix: Force the content div inside expanded expander to be wider */
    div[data-testid="stExpander"][aria-expanded="true"] > div:nth-child(2) {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    @media (min-width: 768px) {
        div[data-testid="stExpander"][aria-expanded="true"] > div:nth-child(2) {
            width: 800px !important;
            max-width: 800px !important;
        }
    }
    
    /* Remove space between task buttons */
    div[data-testid="element-container"]:has(div[data-testid="stExpander"]) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Ensure all text is black */
    .stExpander p, 
    .stExpander div,
    .stTab p, 
    .stTab div {
        color: black !important;
    }
    
    /* Make download and delete buttons full width */
    .stExpander .stButton button {
        width: 100% !important;
    }
    
    /* Force the content columns to use appropriate width */
    div[data-testid="stExpander"][aria-expanded="true"] [data-testid="column"] {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    @media (min-width: 768px) {
        div[data-testid="stExpander"][aria-expanded="true"] [data-testid="column"] {
            width: 390px !important;
            max-width: 390px !important;
        }
    }
    
    /* Stack image and analysis columns on mobile */
    @media (max-width: 767px) {
        div[data-testid="stExpander"] [data-testid="column"] {
            display: block !important;
            width: 100% !important;
        }
    }
    
    /* Fix layout for image and analysis columns */
    .image-column, .analysis-column {
        width: 100% !important;
        max-width: 100% !important;
        padding: 5px !important;
    }
    
    @media (min-width: 768px) {
        .image-column, .analysis-column {
            width: 390px !important;
            max-width: 390px !important;
        }
    }
    
    /* Make images responsive within task history */
    div[data-testid="stImage"] {
        max-width: 100% !important;
    }
    
    div[data-testid="stImage"] img {
        max-width: 100% !important;
        height: auto !important;
        object-fit: contain !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title centered
    st.markdown('<h1 class="centered-title">EstateGeniusAI</h1>', unsafe_allow_html=True)
    
    # Welcome message centered
    st.markdown(f'<p class="centered-title">Welcome, {username}!</p>', unsafe_allow_html=True)
    
    # Start centered content container
    st.markdown('<div class="centered-content">', unsafe_allow_html=True)
    
    # Task selection header
    st.subheader("Select Task Type")
    
    # Task buttons stacked vertically and centered
    st.button("Bulk Upload", use_container_width=True, key="bulk_upload_btn", 
              on_click=lambda: setattr(st.session_state, "page", "bulk_upload"))
    
    st.button("Single Upload", use_container_width=True, key="single_upload_btn",
              on_click=lambda: setattr(st.session_state, "page", "single_upload"))
    
    # Initialize task history toggle state if not present
    if 'show_task_history' not in st.session_state:
        st.session_state.show_task_history = False
    
    # Function to toggle task history
    def toggle_task_history():
        st.session_state.show_task_history = not st.session_state.show_task_history
    
    # Task history button that toggles visibility
    st.button("Task History", use_container_width=True, key="task_history_btn", 
              on_click=toggle_task_history)
    
    # Close centered content container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialize session state for active task if not present
    if 'active_task' not in st.session_state:
        st.session_state.active_task = None
    
    # Add scroll to top button
    scroll_to_top_button()
    
    # Only display task history when toggle is True
    if st.session_state.show_task_history:
        # Task history header (centered)
        st.markdown('<h2 class="centered-title">Task History</h2>', unsafe_allow_html=True)
        
        tasks_df = db.get_user_tasks(st.session_state.user_id)
        
        if tasks_df.empty:
            # Center this message
            st.markdown('<div class="centered-content"><p>No tasks found in your history.</p></div>', unsafe_allow_html=True)
        else:
            # Display each task as expander with consistent sizing
            for idx, task in tasks_df.iterrows():
                # Format task name for display - use task name if available, otherwise use task ID
                display_name = (task['task_name'] if task['task_name'] else f"Task #{task['id']}")
                
                # Format timestamp for display
                task_time = task['created_at']
                if isinstance(task_time, str):
                    # If it's already a string, try to parse it
                    try:
                        from datetime import datetime
                        task_time = datetime.strptime(task_time, '%Y-%m-%d %H:%M:%S')
                        time_display = task_time.strftime('%b %d, %Y - %H:%M')
                    except:
                        time_display = task_time
                else:
                    # Format datetime object
                    time_display = task_time.strftime('%b %d, %Y - %H:%M')
                
                # Function to toggle active task
                def toggle_task(task_id):
                    if st.session_state.active_task == task_id:
                        st.session_state.active_task = None
                    else:
                        st.session_state.active_task = task_id
                
                # Check if this task is active (expanded)
                is_expanded = st.session_state.active_task == task['id']
                
                # Display task in expander with delete option
                with st.expander(f"{display_name} ({time_display})", expanded=is_expanded):
                    # If clicked and wasn't already expanded, make it the active task
                    if not is_expanded and st.session_state.active_task != task['id']:
                        st.session_state.active_task = task['id']
                    
                    # Task details - Using st.write for proper rendering
                    st.write(f"**Type:** {task['task_type'].capitalize()}")
                    
                    if task['task_description']:
                        st.write(f"**Description:** {task['task_description']}")
                    
                    st.write(f"**Created:** {task['created_at']}")
                    st.write(f"**Status:** {task['status']}")
                    st.write(f"**Images:** {task['image_count']}")
                    
                    # Show progress for tasks being processed
                    if task['status'] in ['processing', 'pending', 'partially_processed', 'needs_review']:
                        if 'processed_count' in task:
                            progress = task['processed_count'] / task['image_count'] if task['image_count'] > 0 else 0
                            st.progress(progress, text=f"Processed {task['processed_count']} of {task['image_count']} images")
                    
                    if task['status'] == 'completed':
                        st.write(f"**Completed:** {task['completed_at']}")
                        
                        if task['task_type'] == 'bulk' and task['output_path']:
                            with open(task['output_path'], "rb") as file:
                                st.download_button(
                                    label="Download Report",
                                    data=file,
                                    file_name=os.path.basename(task['output_path']),
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                    
                    # Allow user to mark task as complete if it's in review status
                    if task['status'] == 'needs_review':
                        if st.button("Mark as Complete", key=f"complete_{task['id']}"):
                            if processing.mark_task_complete(task['id']):
                                st.success("Task marked as complete!")
                            else:
                                st.error("Failed to mark task as complete")
                    
                    # Load images and their analysis explicitly, whether expanded or not
                    images_df = db.get_image_analysis(task['id'])
                    
                    if not images_df.empty:
                        # Always display results header
                        st.subheader("Results")
                        
                        # Mobile-first approach: on mobile devices, stack images and analysis
                        for i, img in enumerate(images_df.itertuples()):
                            # Add a separator between images
                            if i > 0:
                                st.markdown("---")
                            
                            # Use columns for desktop but stack for mobile
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown('<div class="image-column">', unsafe_allow_html=True)
                                try:
                                    image = Image.open(img.image_path)
                                    # Use column width instead of fixed width for responsiveness
                                    st.image(image, use_column_width=True)
                                    st.write(f"**Description:** {img.description if img.description else 'None'}")
                                except Exception as e:
                                    st.error(f"Error loading image: {e}")
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown('<div class="analysis-column">', unsafe_allow_html=True)
                                # Show analysis directly
                                if img.analysis:
                                    st.write("**Analysis:**")
                                    st.write(img.analysis)
                                else:
                                    st.info("No analysis available")
                                st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display delete task button
                    def set_delete_task(task_id, task_name):
                        st.session_state.confirm_delete_task = task_id
                        st.session_state.confirm_delete_name = task_name
                    
                    st.button("Delete Task", key=f"delete_{task['id']}", 
                              on_click=set_delete_task, 
                              args=(task['id'], display_name),
                              use_container_width=True)
            
            # Handle delete confirmation if needed
            if 'confirm_delete_task' in st.session_state and st.session_state.confirm_delete_task:
                task_id = st.session_state.confirm_delete_task
                task_name = st.session_state.confirm_delete_name
                
                # Show confirmation dialog in a centered container - responsive
                st.markdown('<div style="max-width: 100%; margin: 0 auto;">', unsafe_allow_html=True)
                st.warning(f"Are you sure you want to delete task {task_name}? This will remove all images and reports.")
                
                col1, col2 = st.columns(2)
                
                def confirm_delete():
                    if db.delete_task(st.session_state.confirm_delete_task):
                        # If the active task was deleted, clear it
                        if st.session_state.active_task == st.session_state.confirm_delete_task:
                            st.session_state.active_task = None
                        # Clear the confirmation state
                        del st.session_state.confirm_delete_task
                        del st.session_state.confirm_delete_name
                
                def cancel_delete():
                    # Clear the confirmation state
                    del st.session_state.confirm_delete_task
                    del st.session_state.confirm_delete_name
                
                with col1:
                    if st.button("Yes, delete", key="confirm_delete", on_click=confirm_delete):
                        pass  # Action handled in callback
                
                with col2:
                    if st.button("Cancel", key="cancel_delete", on_click=cancel_delete):
                        pass  # Action handled in callback
                
                st.markdown('</div>', unsafe_allow_html=True)

# Finally, let's modify the display_formatted_analysis function to ensure responsive text

def display_formatted_analysis(analysis_text):
    """Display the analysis in a formatted way with proper text color and responsive layout"""
    # Import colors from config
    from config import COLOR_THEME as colors
    
    if not analysis_text:
        st.info("No analysis available.")
        return
    
    # Wrap the entire analysis in a div with styling using the config color
    st.markdown(f'<div class="analysis-results" style="color: {colors["ANALYSIS_TEXT_COLOR"]}; width: 100%; max-width: 100%;">', unsafe_allow_html=True)
    
    # Handle the raw analysis string properly
    lines = analysis_text.split('\n')
    current_section = None
    
    for line in lines:
        # Check if this is a section header (all caps followed by colon)
        if line.strip().upper() == line.strip() and ':' in line:
            current_section = line.strip()
            # Display section headers with the analysis color, not the heading color
            st.markdown(f'<h3 style="color: {colors["ANALYSIS_TEXT_COLOR"]};">{current_section}</h3>', unsafe_allow_html=True)
        
        # Check if this is a bullet point
        elif line.strip().startswith('- '):
            st.markdown(f'<p style="color: {colors["ANALYSIS_TEXT_COLOR"]}; word-wrap: break-word;">{line}</p>', unsafe_allow_html=True)
        
        # Regular text line
        elif line.strip():
            st.markdown(f'<p style="color: {colors["ANALYSIS_TEXT_COLOR"]}; word-wrap: break-word;">{line}</p>', unsafe_allow_html=True)
    
    # Close the wrapper div
    st.markdown('</div>', unsafe_allow_html=True)

def admin_page():
    """Admin page for managing users and system settings"""
    # Check if user is admin
    user_info = db.get_user_info(st.session_state.user_id)
    
    if not user_info or not user_info.get("is_admin", False):
        st.error("Access denied. You don't have administrator privileges.")
        st.button("Back to Home", on_click=lambda: setattr(st.session_state, "page", "home"))
        return
    
    # Display user information in the header
    display_user_header()
    
    st.title("Admin Panel")
    
    # Add scroll to top button
    scroll_to_top_button()
    
    # Create tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs(["User Management", "System Settings", "Task Management", "Admin Access"])
    
    with tab1:
        st.header("User Management")
        
        # Get all users
        conn = sqlite3.connect(config.DATABASE_PATH)
        users_df = pd.read_sql_query(
            "SELECT id, username, image_quota, images_processed, is_admin FROM users ORDER BY username",
            conn
        )
        conn.close()
        
        if users_df.empty:
            st.info("No users found.")
        else:
            # Display users in a table
            st.dataframe(users_df, use_container_width=True)
            
            # User quota management
            st.subheader("Update User Quota")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                selected_user = st.selectbox(
                    "Select User", 
                    options=users_df['id'].tolist(),
                    format_func=lambda x: f"{users_df[users_df['id'] == x]['username'].iloc[0]} (ID: {x})",
                    key="quota_user_select" 
                )
            
            with col2:
                # Get current quota for the selected user
                current_quota = users_df[users_df['id'] == selected_user]['image_quota'].iloc[0]
                new_quota = st.number_input("New Quota", min_value=0, value=current_quota)
            
            with col3:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("Update Quota", use_container_width=True):
                    if db.update_user_quota(selected_user, new_quota):
                        st.success(f"Updated quota for user ID {selected_user} to {new_quota}")
                        st.rerun()
                    else:
                        st.error("Failed to update quota")
            
            # Reset user usage
            st.subheader("Reset User Usage")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                reset_user = st.selectbox(
                    "Select User to Reset", 
                    options=users_df['id'].tolist(),
                    format_func=lambda x: f"{users_df[users_df['id'] == x]['username'].iloc[0]} (ID: {x}) - Used: {users_df[users_df['id'] == x]['images_processed'].iloc[0]}",
                    key="reset_user"
                )
            
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("Reset Usage", use_container_width=True):
                    if db.reset_user_usage(reset_user):
                        st.success(f"Reset usage count for user ID {reset_user}")
                        st.rerun()
                    else:
                        st.error("Failed to reset usage")
    
    with tab2:
        st.header("System Settings")
        
        # Get current settings
        max_bulk_upload = int(db.get_system_setting('max_bulk_upload', 25))
        default_user_quota = int(db.get_system_setting('default_user_quota', 100))
        
        # Max bulk upload setting
        st.subheader("Maximum Bulk Upload Size")
        new_max_bulk = st.number_input(
            "Maximum images per bulk upload", 
            min_value=1, 
            max_value=500,
            value=max_bulk_upload
        )
        
        if st.button("Update Bulk Upload Limit"):
            if db.update_system_setting('max_bulk_upload', str(new_max_bulk)):
                st.success(f"Updated maximum bulk upload size to {new_max_bulk}")
            else:
                st.error("Failed to update setting")
        
        # Default user quota setting
        st.subheader("Default User Quota")
        new_default_quota = st.number_input(
            "Default image quota for new users", 
            min_value=0,
            value=default_user_quota
        )
        
        if st.button("Update Default Quota"):
            if db.update_system_setting('default_user_quota', str(new_default_quota)):
                st.success(f"Updated default user quota to {new_default_quota}")
            else:
                st.error("Failed to update setting")
    
    with tab3:
        st.header("Task Management")
        
        # Get all tasks
        conn = sqlite3.connect(config.DATABASE_PATH)
        tasks_df = pd.read_sql_query(
            """
            SELECT t.id, t.task_type, t.task_name, t.status, t.created_at, 
                   u.username as user, COUNT(i.id) as image_count
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            LEFT JOIN images i ON t.id = i.task_id
            GROUP BY t.id
            ORDER BY t.created_at DESC
            LIMIT 100
            """,
            conn
        )
        conn.close()
        
        if tasks_df.empty:
            st.info("No tasks found.")
        else:
            # Filter options
            st.subheader("Filter Tasks")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.multiselect(
                    "Status", 
                    options=['pending', 'processing', 'needs_review', 'partially_processed', 'completed', 'failed', 'cancelled'],
                    default=[]
                )
            
            with col2:
                task_type_filter = st.multiselect(
                    "Task Type",
                    options=['bulk', 'single'],
                    default=[]
                )
            
            with col3:
                search_term = st.text_input("Search by Task Name")
            
            # Apply filters
            filtered_df = tasks_df.copy()
            
            if status_filter:
                filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
            
            if task_type_filter:
                filtered_df = filtered_df[filtered_df['task_type'].isin(task_type_filter)]
            
            if search_term:
                filtered_df = filtered_df[filtered_df['task_name'].str.contains(search_term, case=False, na=False)]
            
            # Display tasks
            st.dataframe(filtered_df, use_container_width=True)
            
            # Task action section
            st.subheader("Task Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Mark task as complete
                st.write("Complete Task")
                complete_task_id = st.selectbox(
                    "Select Task to Complete",
                    options=filtered_df[filtered_df['status'].isin(['needs_review', 'partially_processed'])]['id'].tolist(),
                    format_func=lambda x: f"ID: {x} - {filtered_df[filtered_df['id'] == x]['task_name'].iloc[0]} ({filtered_df[filtered_df['id'] == x]['status'].iloc[0]})",
                    key="admin_complete_task_select"
                )
                
                if st.button("Mark as Complete", key="admin_complete"):
                    if processing.mark_task_complete(complete_task_id):
                        st.success(f"Task {complete_task_id} marked as complete")
                        st.rerun()
                    else:
                        st.error("Failed to mark task as complete")
            
            with col2:
                # Cancel task
                st.write("Cancel Task")
                cancel_task_id = st.selectbox(
                    "Select Task to Cancel",
                    options=filtered_df[filtered_df['status'].isin(['pending', 'processing'])]['id'].tolist(),
                    format_func=lambda x: f"ID: {x} - {filtered_df[filtered_df['id'] == x]['task_name'].iloc[0]} ({filtered_df[filtered_df['id'] == x]['status'].iloc[0]})",
                    key="admin_cancel_task_select"
                )
                
                if st.button("Cancel Task", key="admin_cancel"):
                    if processing.cancel_task(cancel_task_id):
                        st.success(f"Task {cancel_task_id} has been cancelled")
                        st.rerun()
                    else:
                        st.error("Failed to cancel task")
            
            # Delete task
            st.write("Delete Task")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                delete_task_id = st.selectbox(
                    "Select Task to Delete",
                    options=filtered_df['id'].tolist(),
                    format_func=lambda x: f"ID: {x} - {filtered_df[filtered_df['id'] == x]['task_name'].iloc[0]} ({filtered_df[filtered_df['id'] == x]['status'].iloc[0]})",
                    key="admin_delete_task_select"
                )
            
            with col2:
                st.write("")  # Spacing
                if st.button("Delete Task", key="admin_delete"):
                    if db.delete_task(delete_task_id):
                        st.success(f"Task {delete_task_id} has been deleted")
                        st.rerun()
                    else:
                        st.error("Failed to delete task")
    
    with tab4:
        st.header("Admin Access Management")
        
        # Get all users
        conn = sqlite3.connect(config.DATABASE_PATH)
        users_df = pd.read_sql_query(
            "SELECT id, username, is_admin FROM users ORDER BY username",
            conn
        )
        conn.close()
        
        if users_df.empty:
            st.info("No users found.")
        else:
            # Display current admins
            st.subheader("Current Administrators")
            admin_users = users_df[users_df['is_admin'] == 1]
            
            if admin_users.empty:
                st.warning("No administrators found in the system.")
            else:
                st.dataframe(admin_users[['id', 'username']], use_container_width=True)
            
            # Grant admin privileges
            st.subheader("Manage Admin Access")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                selected_user = st.selectbox(
                    "Select User", 
                    options=users_df['id'].tolist(),
                    format_func=lambda x: f"{users_df[users_df['id'] == x]['username'].iloc[0]} (ID: {x})",
                    key="admin_user_select"  # Add this unique key
                )
            
            with col2:
                # Get current admin status
                is_admin = users_df[users_df['id'] == selected_user]['is_admin'].iloc[0] == 1
                admin_status = st.checkbox("Admin Access", value=is_admin)
            
            with col3:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("Update Access", use_container_width=True):
                    if db.set_admin_status(selected_user, admin_status):
                        st.success(f"Updated admin status for user ID {selected_user}")
                        st.rerun()
                    else:
                        st.error("Failed to update admin status")
            
            # Create admin user
            st.subheader("Create New Admin User")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_admin_username = st.text_input("Username")
                new_admin_password = st.text_input("Password", type="password")
            
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("Create Admin User", use_container_width=True):
                    if new_admin_username and new_admin_password:
                        if db.create_user(new_admin_username, new_admin_password, is_admin=True):
                            st.success(f"Created new admin user: {new_admin_username}")
                            st.rerun()
                        else:
                            st.error("Username already exists")
                    else:
                        st.error("Username and password are required")


def display_user_header():
    """Display user information, quota, and logout button in header without progress bar"""
    # Get user information
    user_info = db.get_user_info(st.session_state.user_id)
    
    if not user_info:
        return
    
    # Create a container for the header
    header_container = st.container()
    
    with header_container:
        # Apply CSS for header layout
        st.markdown("""
        <style>
        .user-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 16px;
            margin-bottom: 10px;
        }
        .user-info {
            display: flex;
            align-items: center;
        }
        .username {
            margin-right: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create a row with user info and logout button
        cols = st.columns([2, 2, 1])
        
        with cols[0]:
            # Username
            st.write(f"**User:** {user_info['username']}")
        
        with cols[1]:
            # Quota (without progress bar)
            quota_used = user_info["images_processed"]
            quota_total = user_info["image_quota"]
            st.write(f"**Quota:** {quota_used}/{quota_total}")
        
        with cols[2]:
            # Admin link and logout buttons
            if user_info.get("is_admin", False):
                admin_col, logout_col = st.columns(2)
                with admin_col:
                    if st.button("Admin", key="admin_link"):
                        st.session_state.page = "admin"
                        st.rerun()
                with logout_col:
                    if st.button("Logout", key="logout_btn"):
                        st.session_state.user_id = None
                        st.rerun()
            else:
                # Just logout button
                if st.button("Logout", key="logout_btn"):
                    st.session_state.user_id = None
                    st.rerun()
                
    # Add separator after header
    st.markdown("---")

def scroll_to_top_button():
    """Add a scroll to top button that appears when scrolling down"""
    st.markdown("""
    <style>
    .scroll-to-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #4CAF50;
        color: white;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        text-align: center;
        line-height: 50px;
        font-size: 24px;
        cursor: pointer;
        z-index: 9999;
        display: none;
    }
    </style>
    
    <script>
    // Create scroll to top button
    var scrollButton = document.createElement("DIV");
    scrollButton.className = "scroll-to-top";
    scrollButton.innerHTML = "⬆";
    document.body.appendChild(scrollButton);
    
    // Show/hide button based on scroll position
    window.onscroll = function() {
        if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
            scrollButton.style.display = "block";
        } else {
            scrollButton.style.display = "none";
        }
    };
    
    // Scroll to top when clicked
    scrollButton.onclick = function() {
        document.body.scrollTop = 0; // For Safari
        document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
    };
    </script>
    """, unsafe_allow_html=True)

def display_task_history():
    """Display the user's task history with collapsible sections and compact width"""
    st.header("Task History")
    
    tasks_df = db.get_user_tasks(st.session_state.user_id)
    
    if tasks_df.empty:
        st.info("No tasks found in your history.")
        return
    
    # Create a container with restricted width
    with st.container():
        # Add custom CSS to restrict width
        st.markdown("""
        <style>
        .task-history-container {
            max-width: 650px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Apply the class to a div container
        st.markdown('<div class="task-history-container">', unsafe_allow_html=True)
        
        for _, task in tasks_df.iterrows():
            # Each task is in an expander that is closed by default
            with st.expander(f"Task #{task['id']} - {task['task_type'].capitalize()} ({task['status']})", expanded=False):
                st.write(f"Created: {task['created_at']}")
                st.write(f"Status: {task['status']}")
                st.write(f"Images: {task['image_count']}")
                
                if task['status'] == 'completed':
                    st.write(f"Completed: {task['completed_at']}")
                    
                    if task['task_type'] == 'bulk' and task['output_path']:
                        with open(task['output_path'], "rb") as file:
                            st.download_button(
                                label="Download Report",
                                data=file,
                                file_name=os.path.basename(task['output_path']),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                
                # Display images for this task - only if expanded
                images_df = db.get_image_analysis(task['id'])
                
                if not images_df.empty:
                    st.subheader("Results")
                    
                    # Display results in a table
                    results_table = []
                    for _, img in images_df.iterrows():
                        try:
                            image = Image.open(img['image_path'])
                            # Convert PIL image to bytes for st.image
                            img_byte_arr = io.BytesIO()
                            image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                            img_byte_arr = img_byte_arr.getvalue()
                            
                            # Create a row for the table
                            results_table.append({
                                "Image": img_byte_arr,
                                "Description": img['description'] if img['description'] else "None",
                                "Analysis": img['analysis'] if img['analysis'] else "No analysis available"
                            })
                        except Exception as e:
                            st.error(f"Error displaying image: {str(e)}")
                    
                    # Display the tabular results
                    if results_table:
                        # Create tabs for different views
                        tab1, tab2 = st.tabs(["Table View", "Detail View"])
                        
                        with tab1:
                            # Display as a compact table with fixed width
                            for i, result in enumerate(results_table):
                                cols = st.columns([1, 1])  # Equal width columns
                                with cols[0]:
                                    # Image with fixed width of 200px
                                    st.image(result["Image"], width=200)
                                    st.write(f"**Description:** {result['Description']}")
                                with cols[1]:
                                    # Analysis text
                                    st.markdown(result["Analysis"])
                                
                                # Add separator except for last item
                                if i < len(results_table) - 1:
                                    st.markdown("---")
                        
                        with tab2:
                            # Detailed card view with fixed width
                            for result in results_table:
                                with st.container():
                                    st.image(result["Image"], width=200)
                                    st.markdown(f"**Description:** {result['Description']}")
                                    display_formatted_analysis(result["Analysis"])
                                    st.markdown("---")
        
        # Close the container
        st.markdown('</div>', unsafe_allow_html=True)

def single_upload_page():
    """Render the improved single upload page with better camera controls and mobile responsiveness"""
    st.title("Single Upload")
    
    # Back button
    if st.button("Back to Home"):
        st.session_state.page = "home"
        # Make sure to turn off camera when navigating away
        st.session_state.camera_on = False
        # Clear task naming state
        if 'task_name_submitted' in st.session_state:
            del st.session_state.task_name_submitted
        if 'task_name' in st.session_state:
            del st.session_state.task_name
        if 'task_description' in st.session_state:
            del st.session_state.task_description
        st.rerun()
    
    # Add scroll to top button
    scroll_to_top_button()
    
    # If this is first load, show task naming dialog
    if 'task_name_submitted' not in st.session_state:
        st.session_state.task_name_submitted = False
        
    if not st.session_state.task_name_submitted:
        # Force form width with a column
        _, center_col, _ = st.columns([1, 3, 1])
        
        with center_col:
            # Use a form with a border
            with st.form("create_task_form", border=True):
                task_name = st.text_input("Task Name (required)")
                task_description = st.text_area("Task Description (optional)", height=100)
                
                # Create a row of 5 columns for button placement
                cols = st.columns([1, 2, 1, 2, 1])
                
                with cols[1]:
                    continue_btn = st.form_submit_button("Continue", use_container_width=True)
                
                with cols[3]:
                    cancel_btn = st.form_submit_button("Cancel", use_container_width=True)
        
        # Handle form submission
        if continue_btn:
            if not task_name:
                st.error("Task name is required")
            else:
                st.session_state.task_name = task_name
                st.session_state.task_description = task_description
                st.session_state.task_name_submitted = True
                st.rerun()
        
        if cancel_btn:
            st.session_state.page = "home"
            st.rerun()
        
        # Don't show the rest of the page until task name is submitted
        return
    
    # Show task name at the top of the page
    st.info(f"Task: {st.session_state.task_name}")
    
    # Initialize camera state if not present
    if 'camera_on' not in st.session_state:
        st.session_state.camera_on = False
        
    # Initialize file uploader key
    if 'file_uploader_key' not in st.session_state:
        st.session_state.file_uploader_key = 0
    
    # Add Upload Image section with a container that has a border
    with st.container():
        # Add border style in container
        st.markdown("""
        <div style="
            border: 1px solid #E0E0E0; 
            border-radius: 5px; 
            padding: 10px 15px; 
            margin-bottom: 15px;
            background-color: #F9F9F9;">
            <h3 style="margin: 0; color: #C75F42;">Upload Image</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Put a small vertical spacer
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Add CSS to hide the divider on mobile
    st.markdown("""
    <style>
    @media (max-width: 767px) {
        .mobile-hidden {
            display: none !important;
        }
        
        /* On mobile, stack the columns vertically */
        [data-testid="column"]:nth-of-type(1), 
        [data-testid="column"]:nth-of-type(3) {
            width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create three columns to make room for a divider
    left_col, divider_col, right_col = st.columns([10, 1, 10])
    
    with left_col:
        st.subheader("Upload with Camera")
        
        # Add camera toggle buttons - one to turn on and one to turn off
        cam_col1, cam_col2 = st.columns(2)
        
        with cam_col1:
            if not st.session_state.camera_on:
                if st.button("Turn On Camera", key="open_camera_single"):
                    st.session_state.camera_on = True
                    st.rerun()
        
        with cam_col2:
            if st.session_state.camera_on:
                if st.button("Turn Off Camera", key="close_camera_single"):
                    st.session_state.camera_on = False
                    st.rerun()
        
        # Only show camera when toggled on
        if st.session_state.camera_on:
            camera_img = st.camera_input("Take a picture")
            
            if camera_img:
                # Add description
                camera_desc = st.text_input("Enter description (optional)", key="single_camera_desc")
                
                if st.button("Process Image", key="process_camera"):
                    # Turn off camera after processing
                    st.session_state.camera_on = False
                    
                    # Add image to temp task list
                    img_info = processing.add_image_to_current_task(camera_img.getvalue(), camera_desc)
                    st.session_state.current_task_images = [img_info]
                    
                    # Submit single image task
                    task_id = processing.submit_task(
                        st.session_state.user_id, 
                        "single", 
                        st.session_state.current_task_images,
                        st.session_state.task_name,
                        st.session_state.task_description
                    )
                    
                    st.success(f"Image submitted for processing (Task #{task_id})")
                    
                    # Wait for processing to complete
                    with st.spinner("Processing image..."):
                        while True:
                            status = db.get_task_status(task_id)
                            
                            if status == 'completed':
                                break
                            elif status == 'failed':
                                st.error("Processing failed")
                                break
                            
                            time.sleep(2)
                    
                    # Display results
                    images_df = db.get_image_analysis(task_id)
                    
                    if not images_df.empty:
                        analysis = images_df.iloc[0]['analysis']
                        
                        # Add Analysis Results header in a box with custom styling
                        st.markdown("""
                        <div style="
                            border: 1px solid #C75F42; 
                            border-radius: 5px; 
                            padding: 10px 15px; 
                            margin-bottom: 15px;
                            background-color: white;">
                            <h3 style="margin: 0; color: #C75F42;">Analysis Results</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Make image responsive
                        st.image(Image.open(images_df.iloc[0]['image_path']), use_column_width=True)
                        display_formatted_analysis(analysis)
                    
                    # Clear the task list and turn off camera
                    st.session_state.current_task_images = []
                    # Clear task naming state
                    if 'task_name_submitted' in st.session_state:
                        del st.session_state.task_name_submitted
                    if 'task_name' in st.session_state:
                        del st.session_state.task_name
                    if 'task_description' in st.session_state:
                        del st.session_state.task_description
    
    # Add a vertical divider in the middle column - with class for mobile hiding
    with divider_col:
        # This creates a full-height black divider that will be hidden on mobile
        st.markdown("""
        <div class="mobile-hidden" style="background-color: black; width: 1px; height: 300px; margin: 0 auto;"></div>
        """, unsafe_allow_html=True)
    
    with right_col:
        st.subheader("Upload from Gallery")
        
        # Only show file uploader when camera is off
        if not st.session_state.camera_on:
            uploaded_file = st.file_uploader(
                "Choose an image", 
                type=["jpg", "jpeg", "png"],
                key=f"file_uploader_single_{st.session_state.file_uploader_key}"
            )
            
            if uploaded_file:
                # Add description
                gallery_desc = st.text_input("Enter description (optional)", key="single_gallery_desc")
                
                if st.button("Process Image", key="process_gallery"):
                    # Add image to temp task list
                    img_info = processing.add_image_to_current_task(uploaded_file.getbuffer(), gallery_desc)
                    st.session_state.current_task_images = [img_info]
                    
                    # Submit single image task
                    task_id = processing.submit_task(
                        st.session_state.user_id, 
                        "single", 
                        st.session_state.current_task_images,
                        st.session_state.task_name,
                        st.session_state.task_description
                    )
                    
                    st.success(f"Image submitted for processing (Task #{task_id})")
                    
                    # Wait for processing to complete
                    with st.spinner("Processing image..."):
                        while True:
                            status = db.get_task_status(task_id)
                            
                            if status == 'completed':
                                break
                            elif status == 'failed':
                                st.error("Processing failed")
                                break
                            
                            time.sleep(2)
                    
                    # Display results
                    images_df = db.get_image_analysis(task_id)
                    
                    if not images_df.empty:
                        analysis = images_df.iloc[0]['analysis']
                        
                        # Add Analysis Results header in a box with custom styling
                        st.markdown("""
                        <div style="
                            border: 1px solid #C75F42; 
                            border-radius: 5px; 
                            padding: 10px 15px; 
                            margin-bottom: 15px;
                            background-color: white;">
                            <h3 style="margin: 0; color: #C75F42;">Analysis Results</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Make image responsive
                        st.image(Image.open(images_df.iloc[0]['image_path']), use_column_width=True)
                        display_formatted_analysis(analysis)
                    
                    # Clear the task list and reset file uploader
                    st.session_state.current_task_images = []
                    st.session_state.file_uploader_key += 1
                    # Clear task naming state
                    if 'task_name_submitted' in st.session_state:
                        del st.session_state.task_name_submitted
                    if 'task_name' in st.session_state:
                        del st.session_state.task_name
                    if 'task_description' in st.session_state:
                        del st.session_state.task_description
                    st.rerun()
        else:
            # Show a message when camera is on
            st.warning("Please turn off the camera before using gallery upload")

# Update the bulk_upload_page function to be mobile responsive
def bulk_upload_page():
    """Render the improved bulk upload page with better camera controls and mobile responsiveness"""
    st.title("Bulk Upload")
    
    # Back button
    if st.button("Back to Home"):
        st.session_state.page = "home"
        # Make sure to turn off camera when navigating away
        st.session_state.camera_on = False
        # Clear task naming state
        if 'task_name_submitted' in st.session_state:
            del st.session_state.task_name_submitted
        if 'task_name' in st.session_state:
            del st.session_state.task_name
        if 'task_description' in st.session_state:
            del st.session_state.task_description
        st.rerun()
    
    # If this is first load, show task naming dialog
    if 'task_name_submitted' not in st.session_state:
        st.session_state.task_name_submitted = False
        
    if not st.session_state.task_name_submitted:
        # Force form width with a column
        _, center_col, _ = st.columns([1, 3, 1])
        
        with center_col:
            # Use a form with a border
            with st.form("create_task_form", border=True):
                task_name = st.text_input("Task Name (required)")
                task_description = st.text_area("Task Description (optional)", height=100)
                
                # Create a row of 5 columns for button placement
                cols = st.columns([1, 2, 1, 2, 1])
                
                with cols[1]:
                    continue_btn = st.form_submit_button("Continue", use_container_width=True)
                
                with cols[3]:
                    cancel_btn = st.form_submit_button("Cancel", use_container_width=True)
        
        # Handle form submission
        if continue_btn:
            if not task_name:
                st.error("Task name is required")
            else:
                st.session_state.task_name = task_name
                st.session_state.task_description = task_description
                st.session_state.task_name_submitted = True
                st.rerun()
        
        if cancel_btn:
            st.session_state.page = "home"
            st.rerun()
        
        # Don't show the rest of the page until task name is submitted
        return
    
    # Show task name at the top of the page
    st.info(f"Task: {st.session_state.task_name}")
    
    # Initialize camera state if not present
    if 'camera_on' not in st.session_state:
        st.session_state.camera_on = False
    
    # Initialize file uploader key
    if 'file_uploader_key' not in st.session_state:
        st.session_state.file_uploader_key = 0
    
    # Add Images section with a container that has a border
    with st.container():
        # Add border style in container
        st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div:nth-child(7) {
            border: 1px solid #E0E0E0;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 15px;
            background-color: #F9F9F9;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.subheader("Add Images")
    
    # Put a small vertical spacer
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Add CSS to hide the divider on mobile and stack columns
    st.markdown("""
    <style>
    @media (max-width: 767px) {
        .mobile-hidden {
            display: none !important;
        }
        
        /* On mobile, stack the columns vertically */
        [data-testid="column"]:nth-of-type(1), 
        [data-testid="column"]:nth-of-type(3) {
            width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create three columns to make room for a divider
    left_col, divider_col, right_col = st.columns([10, 1, 10])
    
    with left_col:
        st.subheader("Upload with Camera")
        
        # Add camera toggle buttons - one to turn on and one to turn off
        cam_col1, cam_col2 = st.columns(2)
        
        with cam_col1:
            if not st.session_state.camera_on:
                if st.button("Turn On Camera", key="open_camera"):
                    st.session_state.camera_on = True
                    st.rerun()
        
        with cam_col2:
            if st.session_state.camera_on:
                if st.button("Turn Off Camera", key="close_camera"):
                    st.session_state.camera_on = False
                    st.rerun()
        
        # Only show camera when toggled on
        if st.session_state.camera_on:
            camera_img = st.camera_input("Take a picture")
            
            if camera_img:
                # Add description
                camera_desc = st.text_input("Enter description (optional)", key="camera_desc")
                
                if st.button("Add to Bulk Upload", key="add_camera"):
                    img_info = processing.add_image_to_current_task(camera_img.getvalue(), camera_desc)
                    st.session_state.current_task_images.append(img_info)
                    st.success("Image added to bulk upload task")
                    # Don't turn off camera automatically to allow multiple photos
                    st.rerun()
    
    # Add a vertical divider in the middle column - with class for mobile hiding
    with divider_col:
        # This creates a full-height black divider that will be hidden on mobile
        st.markdown("""
        <div class="mobile-hidden" style="background-color: black; width: 1px; height: 300px; margin: 0 auto;"></div>
        """, unsafe_allow_html=True)
    
    with right_col:
        st.subheader("Upload from Gallery")
        
        # Automatically turn off camera when user selects file uploader
        if not st.session_state.camera_on:
            # Normal file uploader flow
            uploaded_file = st.file_uploader(
                "Choose an image", 
                type=["jpg", "jpeg", "png"], 
                key=f"file_uploader_{st.session_state.file_uploader_key}"
            )
            
            if uploaded_file:
                # Add description
                gallery_desc = st.text_input("Enter description (optional)", key="gallery_desc")
                
                if st.button("Add to Bulk Upload", key="add_gallery"):
                    img_info = processing.add_image_to_current_task(uploaded_file.getbuffer(), gallery_desc)
                    st.session_state.current_task_images.append(img_info)
                    st.success("Image added to bulk upload task")
                    # Increment the key to reset the file uploader
                    st.session_state.file_uploader_key += 1
                    st.rerun()
        else:
            # Show a message when camera is on
            st.warning("Please turn off the camera before using gallery upload")
            
    # Display current images in bulk upload task with responsive grid
    if st.session_state.current_task_images:
        # Add Current Task Images header in a box with custom styling
        st.markdown("""
        <div style="
            border: 1px solid #C75F42; 
            border-radius: 9px; 
            padding: -2px -2px; 
            margin-bottom: 15px;
            background-color: white;">
            <h3 style="margin: 0; color: #429FC7;">Current Task Images</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Add responsive grid CSS
        st.markdown("""
        <style>
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            grid-gap: 10px;
            margin-bottom: 20px;
        }
        
        .image-item {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .image-item img {
            width: 60px;
            height: 60px;
            object-fit: cover;
        }
        
        .image-caption {
            font-size: 0.8em;
            text-align: center;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 100%;
        }
        
        /* Desktop specific */
        @media (min-width: 768px) {
            .image-grid {
                grid-template-columns: repeat(6, 1fr);
            }
        }
        </style>
        <div class="image-grid">
        """, unsafe_allow_html=True)
        
        # Create image grid in HTML
        image_items_html = ""
        for i, img in enumerate(st.session_state.current_task_images):
            try:
                from PIL import Image
                import base64
                import io
                
                # Open image and convert to base64 for HTML
                image = Image.open(img["path"])
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Create HTML for this image item
                caption = img["description"] if img["description"] else ""
                image_items_html += f"""
                <div class="image-item">
                    <img src="data:image/jpeg;base64,{img_str}" alt="Upload {i+1}"/>
                    <div class="image-caption">{caption}</div>
                </div>
                """
            except Exception as e:
                pass
        
        # Close the grid
        st.markdown(image_items_html + "</div>", unsafe_allow_html=True)
        
        # Display remove buttons with individual keys
        st.markdown("<h4>Remove Images</h4>", unsafe_allow_html=True)
        
        # Determine how many columns for remove buttons (responsive)
        col_count = 3
        num_rows = (len(st.session_state.current_task_images) + col_count - 1) // col_count
        
        for row in range(num_rows):
            cols = st.columns(col_count)
            for col in range(col_count):
                idx = row * col_count + col
                if idx < len(st.session_state.current_task_images):
                    img = st.session_state.current_task_images[idx]
                    with cols[col]:
                        if st.button(f"Remove #{idx+1}", key=f"remove_{img['id']}", help=f"Remove {img['description'] or 'Untitled'}"):
                            # Remove image from list and file system
                            try:
                                os.remove(img["path"])
                            except:
                                pass
                            st.session_state.current_task_images.pop(idx)
                            st.rerun()
        
        # Submit button
        if st.button("Submit Bulk Upload", use_container_width=True):
            # Always turn off camera when submitting
            st.session_state.camera_on = False
            
            task_id = processing.submit_task(
                st.session_state.user_id, 
                "bulk", 
                st.session_state.current_task_images,
                st.session_state.task_name,
                st.session_state.task_description
            )
            st.success(f"Bulk upload task #{task_id} submitted and processing in the background")
            st.session_state.current_task_images = []
            # Clear task naming state
            if 'task_name_submitted' in st.session_state:
                del st.session_state.task_name_submitted
            if 'task_name' in st.session_state:
                del st.session_state.task_name
            if 'task_description' in st.session_state:
                del st.session_state.task_description
            st.session_state.page = "home"
            st.rerun()