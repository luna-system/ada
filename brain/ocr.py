"""
OCR module for extracting text from images.
Uses Tesseract OCR - no GPU required.
"""
import logging
from io import BytesIO
from typing import Optional

from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Handles text extraction from images using Tesseract OCR."""
    
    def __init__(self):
        """Initialize OCR processor."""
        # Verify Tesseract is installed
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR initialized successfully")
        except Exception as e:
            logger.error(f"Tesseract OCR not available: {e}")
            raise
    
    def extract_text(self, image_bytes: bytes) -> dict:
        """
        Extract text from image bytes.
        
        Args:
            image_bytes: Raw image file bytes
            
        Returns:
            dict with extracted text and metadata
        """
        try:
            # Open image from bytes
            image = Image.open(BytesIO(image_bytes))
            
            # Get image info
            width, height = image.size
            format_name = image.format or "unknown"
            
            logger.info(f"Processing image: {format_name} {width}x{height}")
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image)
            
            # Clean up whitespace
            text = text.strip()
            
            # Get confidence data if available
            try:
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                confidences = [c for c in data['conf'] if c != -1]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            except Exception as e:
                logger.warning(f"Could not get confidence data: {e}")
                avg_confidence = None
            
            result = {
                "text": text,
                "char_count": len(text),
                "line_count": len(text.split('\n')) if text else 0,
                "confidence": avg_confidence,
                "image_format": format_name,
                "image_size": f"{width}x{height}"
            }
            
            logger.info(f"Extracted {result['char_count']} chars with {result['confidence']:.1f}% confidence" if avg_confidence else f"Extracted {result['char_count']} chars")
            
            return result
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise


# Global instance
_ocr_processor: Optional[OCRProcessor] = None


def get_ocr_processor() -> OCRProcessor:
    """Get or create the global OCR processor instance."""
    global _ocr_processor
    if _ocr_processor is None:
        _ocr_processor = OCRProcessor()
    return _ocr_processor
