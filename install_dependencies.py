#!/usr/bin/env python3
"""
Kolekt Dependency Installation Script
Installs all required dependencies and sets up the environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main installation function"""
    print("🚀 Kolekt Dependency Installation")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: You're not in a virtual environment")
        print("   Consider creating one with: python -m venv venv")
        print("   Then activate it and run this script again")
        print()
    
    # Install dependencies
    print("📦 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        return False
    
    # Create necessary directories
    print("📁 Creating necessary directories...")
    directories = ["logs", "uploads", "temp"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("⚠️  .env file not found")
        print("   Please create a .env file with your configuration")
        print("   You can copy from .env.example if it exists")
    else:
        print("✅ .env file found")
    
    # Test imports
    print("🧪 Testing imports...")
    test_imports = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "supabase",
        "requests",
        "python-dotenv"
    ]
    
    failed_imports = []
    for module in test_imports:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError:
            print(f"❌ {module} import failed")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Some imports failed: {', '.join(failed_imports)}")
        print("   Try running: pip install -r requirements.txt")
        return False
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure your .env file with Supabase credentials")
    print("2. Run: python setup_supabase.py")
    print("3. Start the server: python start_kolekt.py")
    print("\n🚀 Ready to launch Kolekt!")

if __name__ == "__main__":
    main()
