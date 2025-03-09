import streamlit as st
import yaml
import logging
import os
import time
from pathlib import Path
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CONNECTIONS_DIR = Path("connections")
CONNECTIONS_DIR.mkdir(parents=True, exist_ok=True)

def get_connection_files():
    """Get sorted connection files with debug logging"""
    try:
        files = [(f, os.path.getctime(f)) for f in CONNECTIONS_DIR.glob("*.yaml")]
        sorted_files = sorted(files, key=lambda x: x[1], reverse=True)
        logger.debug(f"Found {len(sorted_files)} connection files")
        return sorted_files
    except Exception as e:
        logger.error(f"Error listing connection files: {str(e)}")
        return []

def save_connection(content: bytes) -> str:
    """Validate and save connection file with enhanced logging"""
    try:
        logger.debug("Attempting to save connection file")
        config = yaml.safe_load(content)
        
        if 'databases' not in config:
            logger.error("Uploaded file missing 'databases' root key")
            raise ValueError("YAML must contain 'databases' root element")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"connection_{timestamp}.yaml"
        filepath = CONNECTIONS_DIR / filename
        
        with open(filepath, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"Successfully saved connection file: {filename}")
        return filename
        
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML: {str(e)}")
        st.error(f"Invalid YAML format: {str(e)}")
    except Exception as e:
        logger.error(f"Save failed: {str(e)}")
        st.error(f"Failed to save connection: {str(e)}")
    return None

def connection_manager():
    """Connection manager component with debug logging"""
    logger.debug("Rendering connection manager")
    st.sidebar.header("Database Connection Manager")
    
    # File upload section
    uploaded_file = st.sidebar.file_uploader(
        "Upload Custom Configuration",
        type=["yaml"],
        key=f"uploader_{uuid.uuid4()}"
    )
    
    if uploaded_file:
        print("File upload detected")
        with st.sidebar.status("Processing..."):
            try:
                file_content = uploaded_file.getvalue()
                logger.debug(f"Received file size: {len(file_content)} bytes")
                
                if saved_name := save_connection(file_content):
                    st.success(f"Success! File saved as: {saved_name}")
                    time.sleep(1)  # Allow filesystem to update
                    logger.debug("Triggering rerun after successful upload")
                    st.rerun()
                else:
                    logger.warning("File upload failed validation")
                    st.error("Failed to save connection file")
                    
            except Exception as e:
                logger.error(f"Upload processing failed: {str(e)}")
                st.error(f"Error processing file: {str(e)}")

    # Connection file selection
    try:
        conn_files = get_connection_files()
        file_names = [f[0].name for f in conn_files]
        logger.debug(f"Available connection files: {file_names}")
        
        selected_file = st.sidebar.selectbox(
            "Available Configurations",
            options=file_names,
            key=f"conn_sel_{uuid.uuid4()}"
        )
        
        if selected_file:
            print(f"Selected configuration: {selected_file}")
            with open(CONNECTIONS