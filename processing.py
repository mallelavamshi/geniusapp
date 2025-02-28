import requests
import base64
import io
import json
from PIL import Image
import time
import anthropic
import os
import queue
import threading
import uuid
from datetime import datetime
import pandas as pd
import logging

# Import local modules
import database as db
import reports
import config
import utils

# Get logger
logger = logging.getLogger(__name__)

# Global processing queue
task_queue = queue.Queue()
processing_tasks = {}

def upload_to_imgbb(image_data, api_key):
    """Upload image to ImgBB and return the URL"""
    url = "https://api.imgbb.com/1/upload"
    payload = {
        'key': api_key,
        'expiration': config.IMGBB_EXPIRATION,
        'image': base64.b64encode(image_data).decode('utf-8')
    }
    
    # Retry mechanism for API calls
    for attempt in range(config.MAX_RETRIES):
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                return response.json()['data']['url']
            else:
                logger.error(f"ImgBB upload error (attempt {attempt+1}): {response.text}")
                time.sleep(config.RETRY_DELAY)
        except Exception as e:
            logger.error(f"ImgBB upload exception (attempt {attempt+1}): {str(e)}")
            time.sleep(config.RETRY_DELAY)
    
    return None

def search_api_analysis(imgbb_url, description="", api_key=""):
    """Get image analysis from SearchAPI"""
    url = "https://www.searchapi.io/api/v1/search"
    
    # Prepare search parameters
    params = config.SEARCHAPI_PARAMS.copy()
    params.update({
        "q": description if description else " ",
        "url": imgbb_url,
        "api_key": api_key
    })
    
    # Retry mechanism for API calls
    for attempt in range(config.MAX_RETRIES):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"SearchAPI error (attempt {attempt+1}): {response.text}")
                time.sleep(config.RETRY_DELAY)
        except Exception as e:
            logger.error(f"SearchAPI exception (attempt {attempt+1}): {str(e)}")
            time.sleep(config.RETRY_DELAY)
    
    return None


def claude_analysis(search_results, api_key=""):
    """Get deeper analysis from Claude API using only first 15 search results"""
    # Extract relevant information from search results
    filtered_results = []
    if 'visual_matches' in search_results and search_results['visual_matches']:
        for match in search_results['visual_matches']:
            filtered_match = {
                'title': match.get('title', ''),
                'source': match.get('source', ''),
                'price': match.get('price', ''),
                'currency': match.get('currency', ''),
                'extracted_price': match.get('extracted_price', '')
            }
            filtered_results.append(filtered_match)
    
    # Limit to first 15 results
    filtered_results = filtered_results[:15]
    
    # Convert filtered results to a JSON string to ensure we're not passing a list directly
    filtered_results_json = json.dumps(filtered_results, indent=2)
    
    # Format prompt with filtered results
    prompt = config.CLAUDE_PROMPT_TEMPLATE.format(
        search_results=filtered_results_json
    )
    
    # Retry mechanism for API calls
    for attempt in range(config.MAX_RETRIES):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            message = client.messages.create(
                model=config.DEFAULT_CLAUDE_MODEL,
                max_tokens=config.MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Get the text content from the response
            if hasattr(message, 'content') and message.content:
                # If content is a list of blocks, extract text from them
                if isinstance(message.content, list):
                    full_text = ""
                    for block in message.content:
                        if hasattr(block, 'text'):
                            full_text += block.text + "\n\n"
                        elif isinstance(block, dict) and 'text' in block:
                            full_text += block['text'] + "\n\n"
                    return full_text.strip()
                # If content is a string, return it directly
                elif isinstance(message.content, str):
                    return message.content
                # If content is a single block object, extract its text
                elif hasattr(message.content, 'text'):
                    return message.content.text
                # Last resort: convert whatever we got to string
                return str(message.content)
            else:
                return "Analysis unavailable: No content in response"
                
        except Exception as e:
            logger.error(f"Claude API error (attempt {attempt+1}): {str(e)}")
            time.sleep(config.RETRY_DELAY)
    
    return "Analysis failed after multiple attempts"

def resize_image(img_data, max_size=None):
    """Resize image while maintaining aspect ratio"""
    if max_size is None:
        max_size = config.THUMBNAIL_SIZE
        
    img = Image.open(io.BytesIO(img_data))
    img.thumbnail(max_size)
    buffered = io.BytesIO()
    img.save(buffered, format=img.format if img.format else "JPEG")
    return buffered.getvalue()

def process_task(task_id, api_keys):
    """Process a task in the background"""
    try:
        # Get task information
        task_type = db.get_task_type(task_id)
        
        if not task_type:
            return
        
        # Update task status to processing
        db.update_task_status(task_id, 'processing')
        
        # Get images for this task
        images_df = db.get_task_images(task_id)
        
        for _, img_row in images_df.iterrows():
            try:
                # Upload to ImgBB
                with open(img_row['image_path'], 'rb') as img_file:
                    img_data = img_file.read()
                
                imgbb_url = upload_to_imgbb(img_data, api_keys['IMGBB_API_KEY'])
                
                if imgbb_url:
                    # Update image record with ImgBB URL
                    db.update_image_with_imgbb_url(img_row['id'], imgbb_url)
                    
                    # Get SearchAPI analysis
                    search_results = search_api_analysis(
                        imgbb_url, 
                        img_row['description'], 
                        api_keys['SEARCHAPI_API_KEY']
                    )
                    
                    if search_results:
                        # Get Claude analysis for this single image
                        analysis = claude_analysis(search_results, api_keys['ANTHROPIC_API_KEY'])
                        
                        # Update image record with analysis - this should be a string now
                        db.update_image_with_analysis(img_row['id'], analysis)
            except Exception as e:
                logger.error(f"Error processing image {img_row['id']}: {str(e)}")
        
        # Generate reports for bulk upload tasks
        output_path = None
        if task_type == 'bulk':
            # Generate Excel report
            output_path = reports.save_to_excel(task_id)
            
            # Generate HTML report (optional)
            html_path = reports.generate_html_report(task_id)
            
            # Generate CSV report (optional)
            csv_path = reports.generate_csv_report(task_id)
        
        # Update task status to completed
        db.update_task_status(task_id, 'completed', output_path)
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}")
        db.update_task_status(task_id, 'failed')

def task_worker(api_keys):
    """Worker function for processing tasks from the queue - processes one task at a time"""
    while True:
        try:
            # Get task from queue without removing it yet (peek)
            task_id = task_queue.get(timeout=1)
            
            # Mark task as processing
            processing_tasks[task_id] = True
            logger.info(f"Starting processing of task {task_id}")
            
            # Process the task
            process_task(task_id, api_keys)
            
            # Mark task as complete and remove from processing dict
            processing_tasks.pop(task_id, None)
            logger.info(f"Completed processing of task {task_id}")
            
            # Now tell the queue this task is done
            task_queue.task_done()
            
        except queue.Empty:
            time.sleep(1)
        except Exception as e:
            logger.error(f"Task worker error: {str(e)}")
            # If there was a task being processed, mark it as failed
            if 'task_id' in locals() and task_id in processing_tasks:
                try:
                    db.update_task_status(task_id, 'failed')
                    processing_tasks.pop(task_id, None)
                    task_queue.task_done()  # Still mark as done to keep queue moving
                except Exception:
                    pass  # Avoid nested exceptions
            time.sleep(5)

def start_worker_thread(api_keys):
    """Start the background worker thread"""
    # Ensure required directories exist
    utils.ensure_directories()
    
    # Run database migrations if needed
    db.migrate_db()
    
    # Start worker thread
    worker_thread = threading.Thread(
        target=task_worker, 
        args=(api_keys,), 
        daemon=True
    )
    worker_thread.start()
    return worker_thread

def add_image_to_current_task(img_data, description=""):
    """Add an image to the current task and save to disk"""
    img_id = str(uuid.uuid4())
    img_dir = config.UPLOAD_DIR
    os.makedirs(img_dir, exist_ok=True)
    
    img_path = f"{img_dir}/{img_id}.jpg"
    
    # Resize image before saving if it exceeds maximum size
    img = Image.open(io.BytesIO(img_data))
    
    # Convert RGBA to RGB to avoid JPEG saving errors
    if img.mode == 'RGBA':
        # Create a white background image
        background = Image.new('RGB', img.size, (255, 255, 255))
        # Paste the image on the background, using the alpha channel as mask
        background.paste(img, (0, 0), img)
        img = background
    
    img.thumbnail(config.MAX_IMAGE_SIZE)
    img.save(img_path)
    
    return {
        "id": img_id,
        "path": img_path,
        "description": description
    }

def submit_task(user_id, task_type, images, task_name="", task_description=""):
    """Create a new task with images and submit for processing"""
    # Check if user has remaining quota
    if not db.has_remaining_quota(user_id):
        logger.warning(f"User {user_id} has reached their quota limit")
        return -1  # Special error code for quota exceeded
    
    # For bulk uploads, check against the maximum allowed images
    if task_type == 'bulk' and len(images) > db.get_bulk_upload_limit():
        logger.warning(f"Bulk upload exceeds limit: {len(images)} > {db.get_bulk_upload_limit()}")
        return -2  # Special error code for bulk upload limit exceeded
    
    # Create a new task with name and description
    task_id = db.create_new_task(user_id, task_type, task_name, task_description)
    
    # Add images to the task
    for img in images:
        db.add_image_to_task(task_id, img["path"], img["description"])
    
    # Add task to processing queue
    task_queue.put(task_id)
    
    return task_id

def mark_task_complete(task_id):
    """Manually mark a task as completed"""
    # Get the task's output path, if any
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT output_path FROM tasks WHERE id = ?", (task_id,))
    result = c.fetchone()
    output_path = result[0] if result else None
    
    conn.close()
    
    # Update the task status
    return db.manually_complete_task(task_id, output_path)

def cancel_task(task_id):
    """Cancel a task that is in progress or pending"""
    # Mark the task as cancelled in the database
    return db.cancel_task(task_id)