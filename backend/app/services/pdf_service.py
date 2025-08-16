import io
import logging
from typing import List, Optional, Dict, Any
from pypdf import PdfReader
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import models
import crud
from database import get_db
from sqlalchemy.orm import Session

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Service for processing PDF files and extracting text content"""
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf_bytes(self, pdf_content: bytes) -> str:
        """
        Extract text from PDF bytes content
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Extracted text as string
        """
        try:
            # Create a BytesIO object from the PDF content
            pdf_stream = io.BytesIO(pdf_content)
            
            # Read PDF using pypdf
            reader = PdfReader(pdf_stream)
            
            # Extract text from all pages
            text_content = ""
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():  # Only add non-empty pages
                        text_content += f"\n--- Page {page_num + 1} ---\n"
                        text_content += page_text + "\n"
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise Exception(f"PDF processing failed: {str(e)}")
    
    async def process_session_pdfs(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Process all PDF files in a video session and extract their text content
        
        Args:
            session_id: Video session ID
            
        Returns:
            List of dictionaries with file info and extracted text
        """
        try:
            # Get database session
            db = next(get_db())
            
            # Get all files for this session
            files = crud.get_files_by_video_session(db, session_id)
            
            pdf_contents = []
            
            for file in files:
                # Check if file is a PDF
                if file.content_type == "application/pdf":
                    try:
                        logger.info(f"Processing PDF file: {file.original_filename}")
                        
                        # Import storage service here to avoid circular imports
                        from .storage_service import storage_service
                        
                        # Download file content from storage using signed URL and fetch
                        signed_url = storage_service.generate_signed_download_url(file.gcs_filename, 30)
                        
                        # Download file content using the signed URL
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            async with session.get(signed_url) as response:
                                if response.status == 200:
                                    file_content = await response.read()
                                else:
                                    raise Exception(f"Failed to download file: HTTP {response.status}")
                        
                        # Extract text from PDF
                        extracted_text = self.extract_text_from_pdf_bytes(file_content)
                        
                        pdf_info = {
                            "file_id": file.id,
                            "filename": file.original_filename,
                            "text_content": extracted_text,
                            "character_count": len(extracted_text),
                            "status": "success"
                        }
                        
                        pdf_contents.append(pdf_info)
                        logger.info(f"Successfully processed PDF: {file.original_filename} ({len(extracted_text)} characters)")
                        
                    except Exception as e:
                        logger.error(f"Failed to process PDF {file.original_filename}: {e}")
                        pdf_info = {
                            "file_id": file.id,
                            "filename": file.original_filename,
                            "text_content": "",
                            "character_count": 0,
                            "status": "error",
                            "error_message": str(e)
                        }
                        pdf_contents.append(pdf_info)
                else:
                    logger.info(f"Skipping non-PDF file: {file.original_filename} (type: {file.content_type})")
            
            logger.info(f"Processed {len(pdf_contents)} PDF files for session {session_id}")
            return pdf_contents
            
        except Exception as e:
            logger.error(f"Failed to process session PDFs: {e}")
            raise Exception(f"Session PDF processing failed: {str(e)}")
    
    def combine_pdf_texts(self, pdf_contents: List[Dict[str, Any]]) -> str:
        """
        Combine all extracted PDF texts into a single document
        
        Args:
            pdf_contents: List of PDF content dictionaries
            
        Returns:
            Combined text content
        """
        try:
            combined_text = ""
            successful_pdfs = [pdf for pdf in pdf_contents if pdf["status"] == "success"]
            
            if not successful_pdfs:
                return "No PDF content was successfully extracted."
            
            combined_text += f"=== COMBINED PDF CONTENT FROM {len(successful_pdfs)} FILES ===\n\n"
            
            for pdf_info in successful_pdfs:
                combined_text += f"=== FILE: {pdf_info['filename']} ===\n"
                combined_text += f"Character Count: {pdf_info['character_count']}\n\n"
                combined_text += pdf_info['text_content']
                combined_text += "\n\n" + "="*50 + "\n\n"
            
            logger.info(f"Combined {len(successful_pdfs)} PDF files into {len(combined_text)} characters")
            return combined_text
            
        except Exception as e:
            logger.error(f"Failed to combine PDF texts: {e}")
            raise Exception(f"PDF text combination failed: {str(e)}")

# Create a global instance
pdf_service = PDFProcessor()