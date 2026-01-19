import os
import time
from pathlib import Path

# Setup directories
DIRS = ["X", "Y1", "Y2", "Y3/deeply/nested/dir"]
BASE_TIME = time.time() - 100000

def create_file(path_str, content, time_offset=0, chmod=None):
    """Creates a file with specific content, timestamp, and permissions."""
    p = Path(path_str)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    with open(p, "w") as f:
        f.write(content)
    
    mod_time = BASE_TIME + time_offset
    os.utime(p, (mod_time, mod_time))
    
    if chmod:
        os.chmod(p, chmod)
    
    print(f"Created: {p}")

def main():
    print("Generating test environment...")

    # --- SCENARIO 1: Content Duplicates  ---
    # Requirement: Files have same content, different names. Keep NEWER.
    content_A = "This is the unique content for Document A."
    create_file("X/doc_A.txt", content_A, time_offset=100)       # OLDER 
    create_file("Y1/doc_A_copy.txt", content_A, time_offset=500) # NEWER

    # --- SCENARIO 2: Name Conflicts  ---
    # Requirement: Files have same name, but different content. Keep NEWER.
    create_file("X/report.txt", "Old Report Data", time_offset=100)      # OLDER (Delete/Replace)
    create_file("Y2/report.txt", "New Report Data", time_offset=900)     # NEWER (Keep/Move to X)

    # --- SCENARIO 3: Empty & Temporary Files [cite: 21, 23] ---
    # Requirement: Delete empty files and .tmp/.bak files.
    create_file("Y2/empty_file.txt", "", time_offset=200)          # Empty content
    create_file("Y2/cache.tmp", "temporary data", time_offset=200) # .tmp extension
    create_file("X/backup.bak", "backup data", time_offset=200)    # .bak extension

    # --- SCENARIO 4: Tricky Filenames  ---
    # Requirement: Rename files with special chars like : or *
    try:
        create_file("Y1/file:name.txt", "Tricky content", time_offset=300)
        create_file("Y1/money$file.txt", "Cash content", time_offset=300)
        create_file("Y1/star*file.txt", "Star content", time_offset=300)
    except OSError:
        print("Skipped some tricky filenames (OS limitation).")

    # --- SCENARIO 5: Permissions ---
    # Requirement: Fix permissions (e.g., change 777 to 644).
    create_file("Y1/script.sh", "#!/bin/bash", time_offset=400, chmod=0o777)
    
    # --- SCENARIO 6: Consolidation (Deep Nesting) ---
    # Requirement: Move files from Y trees into X.
    create_file("Y3/deeply/nested/dir/deep_data.txt", "Hidden Data", time_offset=600)
    create_file("Y3/simple_note.txt", "Note", time_offset=600)

    print("\nTest files generated successfully.")

if __name__ == "__main__":
    main()