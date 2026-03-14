import zipfile
from io import BytesIO
from typing import List, Tuple
from fastapi import UploadFile


ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.jsx', '.tsx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB


def parse_zip_file(zip_file: UploadFile) -> List[Tuple[str, str]]:
    """Extract files from ZIP upload"""
    files = []
    
    with zipfile.ZipFile(BytesIO(zip_file.file.read())) as zf:
        for filename in zf.namelist():
            if filename.endswith('/'):  # Skip directories
                continue
            
            with zf.open(filename) as f:
                content = f.read().decode('utf-8')
                files.append((filename, content))
    
    return files


def concatenate_code_files(files: List[Tuple[str, str]]) -> str:
    """
    Concatenate files with delimiters.
    Format: [FILE_START:filename]\ncontent\n[FILE_END:filename]
    """
    code_blob = ""
    
    for filename, content in files:
        code_blob += f"[FILE_START:{filename}]\n"
        code_blob += content
        code_blob += f"\n[FILE_END:{filename}]\n\n"
    
    return code_blob


async def concatenate_upload_files(files: List[UploadFile]) -> str:
    """Concatenate uploaded files with delimiters"""
    code_blob = ""
    
    for file in files:
        try:
            # Read content as bytes
            content_bytes = await file.read()
            
            # Decode to string
            if isinstance(content_bytes, bytes):
                content = content_bytes.decode('utf-8')
            elif isinstance(content_bytes, str):
                content = content_bytes
            else:
                raise TypeError(f"Unexpected content type: {type(content_bytes)}")
            
            code_blob += f"[FILE_START:{file.filename}]\n"
            code_blob += content
            code_blob += f"\n[FILE_END:{file.filename}]\n\n"
            
            # Reset file pointer for potential re-reading
            await file.seek(0)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing file {file.filename}: {e}", exc_info=True)
            raise ValueError(f"Failed to process file {file.filename}: {str(e)}")
    
    return code_blob


def validate_file_types(files: List[UploadFile]) -> Tuple[bool, str]:
    """Ensure uploaded files are valid code files"""
    for file in files:
        # Get file extension
        ext = '.' + file.filename.split('.')[-1] if '.' in file.filename else ''
        
        if ext.lower() not in ALLOWED_EXTENSIONS:
            return False, f"File type not allowed: {file.filename}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    return True, ""


async def validate_file_sizes(files: List[UploadFile]) -> Tuple[bool, str]:
    """Validate file sizes (10MB per file, 50MB total)"""
    total_size = 0
    
    for file in files:
        content = await file.read()
        file_size = len(content)
        total_size += file_size
        
        # Reset file pointer
        await file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return False, f"File too large: {file.filename} ({file_size / 1024 / 1024:.2f}MB). Max: 10MB"
    
    if total_size > MAX_TOTAL_SIZE:
        return False, f"Total upload size too large: {total_size / 1024 / 1024:.2f}MB. Max: 50MB"
    
    return True, ""
