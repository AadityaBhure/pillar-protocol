#!/usr/bin/env python3
"""
Verify that the project is ready for Vercel deployment
"""
import os
import json
import sys

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"{status} {filepath}")
    return exists

def check_file_content(filepath, expected_content):
    """Check if file contains expected content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if expected_content in content:
                print(f"✅ {filepath} contains expected content")
                return True
            else:
                print(f"❌ {filepath} missing expected content: {expected_content}")
                return False
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

def main():
    print("🔍 Vercel Deployment Readiness Check\n")
    
    all_good = True
    
    # Check required files
    print("📁 Required Files:")
    all_good &= check_file_exists("vercel.json")
    all_good &= check_file_exists("api/index.py")
    all_good &= check_file_exists("backend/main.py")
    all_good &= check_file_exists("requirements.txt")
    all_good &= check_file_exists(".gitignore")
    all_good &= check_file_exists(".env.example")
    all_good &= check_file_exists("index.html")
    all_good &= check_file_exists("script.js")
    all_good &= check_file_exists("style.css")
    
    print("\n📝 Configuration Files:")
    
    # Check vercel.json
    try:
        with open("vercel.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
            if config.get("builds", [{}])[0].get("src") == "api/index.py":
                print("✅ vercel.json points to api/index.py")
            else:
                print("❌ vercel.json should point to api/index.py")
                all_good = False
    except Exception as e:
        print(f"❌ Error reading vercel.json: {e}")
        all_good = False
    
    # Check api/index.py imports
    all_good &= check_file_content("api/index.py", "from backend.main import app")
    
    # Check .gitignore excludes .env
    all_good &= check_file_content(".gitignore", ".env")
    
    # Check script.js has environment detection
    all_good &= check_file_content("script.js", "API_BASE_URL")
    
    print("\n🔐 Environment Variables:")
    if os.path.exists(".env"):
        print("✅ .env file exists (for local development)")
        print("⚠️  Remember: Add these to Vercel dashboard:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_KEY")
        print("   - GEMINI_API_KEY")
    else:
        print("⚠️  .env file not found (create from .env.example for local dev)")
    
    print("\n📦 Python Dependencies:")
    try:
        with open("requirements.txt", 'r', encoding='utf-8') as f:
            deps = f.read()
            required_deps = ["fastapi", "uvicorn", "supabase", "google-generativeai"]
            for dep in required_deps:
                if dep in deps:
                    print(f"✅ {dep}")
                else:
                    print(f"❌ {dep} missing")
                    all_good = False
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        all_good = False
    
    print("\n" + "="*50)
    if all_good:
        print("🎉 ALL CHECKS PASSED!")
        print("\n✅ Your project is ready for Vercel deployment!")
        print("\n📚 Next steps:")
        print("   1. Push to GitHub: git push origin main")
        print("   2. Deploy on Vercel: vercel.com")
        print("   3. Add environment variables in Vercel dashboard")
        print("\n📖 See DEPLOY_NOW.md for detailed instructions")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("\n⚠️  Please fix the issues above before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
