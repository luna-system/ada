// OCR service for extracting text from images
export interface OCRResult {
  text: string;
  char_count: number;
  line_count: number;
  confidence?: number;
  image_format: string;
  image_size: string;
  filename: string;
}

export async function extractTextFromImage(file: File): Promise<OCRResult> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch('/api/ocr/extract', {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'OCR extraction failed' }));
    throw new Error(errorData.detail || `OCR extraction failed: ${res.statusText}`);
  }

  return res.json();
}
