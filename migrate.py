#!/usr/bin/env python3
"""
Migration script to help users switch from the old monolithic structure to the new modular structure.
"""

import os
import shutil
from pathlib import Path

def backup_old_main():
    """Backup the old main.py file."""
    old_main = Path("app/main.py")
    if old_main.exists():
        backup_path = Path("app/main_old.py")
        shutil.copy2(old_main, backup_path)
        print(f"✅ Backed up old main.py to {backup_path}")
        return True
    return False

def rename_new_main():
    """Rename main_new.py to main.py."""
    new_main = Path("app/main_new.py")
    if new_main.exists():
        main_path = Path("app/main.py")
        if main_path.exists():
            os.remove(main_path)
        shutil.move(new_main, main_path)
        print("✅ Renamed main_new.py to main.py")
        return True
    return False

def check_structure():
    """Check if all required files exist in the new structure."""
    required_files = [
        "app/config.py",
        "app/logger.py", 
        "app/utils.py",
        "app/models.py",
        "app/text_extractor.py",
        "app/middleware.py",
        "app/generators/__init__.py",
        "app/generators/flashcard_generator.py",
        "app/generators/quiz_generator.py",
        "app/generators/exercise_generator.py",
        "app/routes/__init__.py",
        "app/routes/file_processing.py",
        "app/routes/health.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files in new structure:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files present in new structure")
        return True

def main():
    """Main migration function."""
    print("🔄 Starting migration to new modular structure...")
    print()
    
    # Check if new structure is complete
    if not check_structure():
        print("❌ Migration failed: New structure is incomplete")
        return
    
    # Backup old main.py
    backup_old_main()
    
    # Rename new main.py
    if rename_new_main():
        print()
        print("🎉 Migration completed successfully!")
        print()
        print("📋 What changed:")
        print("   - Old main.py backed up to app/main_old.py")
        print("   - New modular structure is now active")
        print("   - API endpoints moved to /api/v1/ prefix")
        print("   - Better error handling and logging")
        print()
        print("🚀 To run the application:")
        print("   python -m app.main")
        print()
        print("📖 See README.md for detailed documentation")
    else:
        print("❌ Migration failed: Could not rename main_new.py")

if __name__ == "__main__":
    main() 