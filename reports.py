import pandas as pd
import os
import io
import base64
from PIL import Image
from datetime import datetime

# Import local modules
import database as db
import config
import utils

def resize_image(image_path, max_size=(200, 200)):
    """Resize image while maintaining aspect ratio"""
    try:
        with open(image_path, 'rb') as f:
            img_data = f.read()
            
        img = Image.open(io.BytesIO(img_data))
        img.thumbnail(max_size)
        buffered = io.BytesIO()
        img.save(buffered, format=img.format if img.format else "JPEG")
        return buffered.getvalue()
    except Exception as e:
        print(f"Error resizing image: {str(e)}")
        return None

def save_to_excel(task_id):
    """Generate Excel report for bulk upload task with improved layout"""
    # Get all images for this task
    images_df = db.get_task_images(task_id)
    
    if images_df.empty:
        return None
    
    # Create a new Excel file
    output_path = f"{config.REPORTS_DIR}/task_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    
    # Prepare data for Excel - we only need image_path and analysis columns
    report_df = pd.DataFrame({
        'Image': images_df['image_path'],
        'Analysis': images_df['analysis']
    })
    
    # Write the DataFrame to Excel without the index
    report_df.to_excel(writer, sheet_name='Analysis', index=False)
    
    # Get workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Analysis']
    
    # Format settings
    worksheet.set_column('A:A', 30)  # Image column width
    worksheet.set_column('B:B', 80)  # Analysis column width
    
    # Text wrap format for analysis column
    wrap_format = workbook.add_format({
        'text_wrap': True, 
        'valign': 'top',
        'align': 'left'
    })
    worksheet.set_column('B:B', 80, wrap_format)
    
    # Add images to the Excel file - first column
    for i, img_path in enumerate(images_df['image_path']):
        try:
            # Row index in Excel (add 1 for header row)
            row_idx = i + 1
            
            # Resize image while maintaining aspect ratio
            img_data = resize_image(img_path, max_size=(200, 200))
            if img_data:
                # Insert image in first column
                worksheet.insert_image(
                    row_idx, 0,  # First column (A)
                    img_path,
                    {
                        'image_data': io.BytesIO(img_data),
                        'x_scale': 0.9,
                        'y_scale': 0.9,
                        'positioning': 1,  # Position image in cell
                        'x_offset': 10,    # Center horizontally
                        'y_offset': 5      # Small top margin
                    }
                )
                
                # Set row height to accommodate image (taller for more analysis text)
                # Get length of analysis text to estimate required height
                analysis_text = images_df.iloc[i]['analysis'] or ''
                text_length = len(analysis_text)
                
                # Calculate row height based on text length (approximate)
                # This is an estimate - may need adjustment based on font size and column width
                if text_length < 200:
                    row_height = 150  # Default for short analysis
                elif text_length < 500:
                    row_height = 200  # Medium analysis
                else:
                    row_height = 300  # Long analysis
                
                # Set row height
                worksheet.set_row(row_idx, row_height)
        except Exception as e:
            logger.error(f"Error adding image to Excel: {str(e)}")
    
    # Save the workbook
    writer.close()
    
    return output_path

def generate_html_report(task_id):
    """Generate an HTML report for viewing in the browser"""
    # Get all images for this task
    images_df = db.get_task_images(task_id)
    
    if images_df.empty:
        return None
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Analysis Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .report-header { text-align: center; margin-bottom: 30px; }
            .image-container { display: flex; margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
            .image-preview { flex: 1; max-width: 200px; }
            .image-preview img { max-width: 100%; height: auto; }
            .image-details { flex: 3; padding-left: 20px; }
            .image-description { color: #666; font-style: italic; margin-bottom: 10px; }
            .image-analysis { background-color: #f9f9f9; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="report-header">
            <h1>Image Analysis Report</h1>
            <p>Task ID: """ + str(task_id) + """</p>
            <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>
    """
    
    for _, img in images_df.iterrows():
        # Create HTML for each image
        img_base64 = utils.image_to_base64(img['image_path'])
        html += f"""
        <div class="image-container">
            <div class="image-preview">
                <img src="data:image/jpeg;base64,{img_base64}" alt="Image">
            </div>
            <div class="image-details">
                <h3>Image Details</h3>
                <div class="image-description">
                    <strong>Description:</strong> {img['description'] if img['description'] else 'No description provided'}
                </div>
                <div class="image-analysis">
                    <strong>Analysis:</strong>
                    <p>{img['analysis'] if img['analysis'] else 'No analysis available'}</p>
                </div>
            </div>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    # Save HTML report
    report_path = f"{config.REPORTS_DIR}/task_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    
    with open(report_path, "w") as f:
        f.write(html)
    
    return report_path

def generate_csv_report(task_id):
    """Generate a CSV report for the task"""
    # Get all images for this task
    images_df = db.get_task_images(task_id)
    
    if images_df.empty:
        return None
    
    # Select and reorder columns for the report
    report_df = images_df[['image_path', 'imgbb_url', 'description', 'analysis']]
    report_df.columns = ['Image Path', 'ImgBB URL', 'Description', 'Analysis']
    
    # Create a CSV file
    output_path = f"{config.REPORTS_DIR}/task_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    
    report_df.to_csv(output_path, index=False)
    
    return output_path