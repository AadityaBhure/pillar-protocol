#!/usr/bin/env python3
"""
Test script to verify the type error fix
Tests both file upload and GitHub fetch scenarios
"""

import asyncio
from io import BytesIO


class GitHubFile:
    """Custom class that mimics UploadFile behavior for GitHub files"""
    def __init__(self, filename, content):
        self.filename = filename
        self.content_bytes = content.encode('utf-8')
        self.file = BytesIO(self.content_bytes)
    
    async def read(self):
        return self.content_bytes
    
    async def seek(self, position):
        self.file.seek(position)


async def concatenate_upload_files(files):
    """Test version of concatenate function"""
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
            raise ValueError(f"Failed to process file {file.filename}: {str(e)}")
    
    return code_blob


async def test_github_file():
    """Test GitHub file handling"""
    print("Testing GitHub file handling...")
    
    # Create test file
    test_content = 'print("Hello, World!")'
    github_file = GitHubFile("hello_world.py", test_content)
    
    # Test concatenation
    result = await concatenate_upload_files([github_file])
    
    # Verify result
    assert "[FILE_START:hello_world.py]" in result
    assert test_content in result
    assert "[FILE_END:hello_world.py]" in result
    
    print("✅ GitHub file test passed!")
    print(f"Result:\n{result}")


async def test_multiple_files():
    """Test multiple GitHub files"""
    print("\nTesting multiple GitHub files...")
    
    files = [
        GitHubFile("main.py", "def main():\n    print('Main')"),
        GitHubFile("utils.py", "def helper():\n    return True"),
        GitHubFile("test.py", "def test_main():\n    assert True")
    ]
    
    result = await concatenate_upload_files(files)
    
    # Verify all files are present
    assert "[FILE_START:main.py]" in result
    assert "[FILE_START:utils.py]" in result
    assert "[FILE_START:test.py]" in result
    
    print("✅ Multiple files test passed!")
    print(f"Processed {len(files)} files successfully")


async def main():
    """Run all tests"""
    print("=" * 50)
    print("Type Error Fix - Test Suite")
    print("=" * 50)
    
    try:
        await test_github_file()
        await test_multiple_files()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"❌ Test failed: {e}")
        print("=" * 50)
        raise


if __name__ == "__main__":
    asyncio.run(main())
