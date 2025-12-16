"""
OCR Specialist - Optical Character Recognition plugin.

Extracts text from images using Tesseract OCR.
No GPU required - runs on CPU.
"""
import logging
from typing import Any

from brain.ocr import get_ocr_processor
from .protocol import (
    Specialist,
    BaseSpecialist,
    SpecialistCapability,
    SpecialistResult,
    SpecialistPriority
)

logger = logging.getLogger(__name__)


class OCRSpecialist(BaseSpecialist):
    """
    OCR specialist for extracting text from images.
    
    Auto-activates when ocr_context is present in request.
    """
    
    def __init__(self):
        capability = SpecialistCapability(
            name="ocr",
            description="Extract text from images using Tesseract OCR",
            version="1.0.0",
            context_priority=SpecialistPriority.HIGH,
            context_icon="📄",
            tags=["vision", "text-extraction", "images"],
            input_schema={
                "type": "object",
                "properties": {
                    "ocr_context": {
                        "type": "object",
                        "description": "OCR extraction result from /v1/ocr/extract endpoint"
                    }
                },
                "required": ["ocr_context"]
            }
        )
        super().__init__(capability)
        
        # Lazy-load OCR processor
        self._processor = None
    
    def should_activate(self, request_context: dict) -> bool:
        """Activate when ocr_context is provided"""
        return request_context.get('ocr_context') is not None
    
    async def process(self, **kwargs) -> SpecialistResult:
        """
        Process OCR context and format for LLM consumption.
        
        Expected kwargs:
            ocr_context: dict with keys:
                - text: extracted text
                - filename: source filename
                - char_count: character count
                - confidence: optional confidence score
                - image_format: image format
                - image_size: image dimensions
        """
        ocr_context = kwargs.get('ocr_context')
        
        if not ocr_context:
            return self.error_result("No OCR context provided", "missing_context")
        
        try:
            # Extract fields
            text = ocr_context.get('text', '').strip()
            filename = ocr_context.get('filename', 'image')
            char_count = ocr_context.get('char_count', len(text))
            confidence = ocr_context.get('confidence')
            
            if not text:
                return self.error_result("No text extracted from image", "empty_extraction")
            
            # Format metadata
            metadata = {
                'filename': filename,
                'chars': char_count
            }
            
            if confidence is not None:
                metadata['confidence'] = f"{confidence:.1f}%"
            
            # Format context for LLM
            context_text = self.format_context(
                title=f"OCR Extracted Text from '{filename}'",
                content=text,
                metadata=metadata
            )
            
            # Return result
            return self.success_result(
                context_text=context_text,
                data={
                    'text': text,
                    'filename': filename,
                    'char_count': char_count,
                    'confidence': confidence
                },
                metadata=metadata
            )
        
        except Exception as e:
            logger.error(f"OCR specialist processing failed: {e}", exc_info=True)
            return self.error_result(f"OCR processing error: {str(e)}", "processing_error")
