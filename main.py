import argparse
import sys
import logging

from click import Path
from pyparsing import List


# --- TERMINAL COLORS ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s' 
)
logger = logging.getLogger("Organizer")

class FileOrganizer:
    def __init__(self, target_dir: str, source_dirs: List[str], config_path: str, auto_mode: bool = False):
        """
        Initializes the Organizer with target directory (X), source directories (Y),
        configuration, and interaction mode.
        """
        self.target_dir = Path(target_dir).resolve()
        self.source_dirs = [Path(d).resolve() for d in source_dirs]
        # All directories combined for general cleaning tasks
        self.all_dirs = [self.target_dir] + self.source_dirs
        
        self.auto_mode = auto_mode
        self.config = self._load_config(config_path)


    def remove_empty_and_temp(self):
        pass

    def sanitize_filenames(self):
        pass

    def fix_permissions(self):
        pass

    def consolidate_and_dedup(self):
        pass

    def _load_config(self, config_path: str):
        pass

# --- MAIN EXECUTION ---
def main():
    parser = argparse.ArgumentParser(description="University Project: File System Organizer")
    
    # Arguments
    parser.add_argument("target_dir", help="Main Catalog X (Destination)")
    parser.add_argument("source_dirs", nargs="*", help="Source Catalogs Y1, Y2... (Sources)")
    
    # Flags matching assignment requirements
    parser.add_argument("-d", "--duplicates", action="store_true", help="Consolidate & Deduplicate (Main Action)")
    parser.add_argument("-e", "--empty", action="store_true", help="Remove empty files")
    parser.add_argument("-t", "--temporary", action="store_true", help="Remove temporary files")
    parser.add_argument("-s", "--sanitize", action="store_true", help="Sanitize filenames (fix tricky chars)")
    parser.add_argument("-p", "--permissions", action="store_true", help="Fix file permissions")
    parser.add_argument("-a", "--all", action="store_true", help="Run ALL operations")
    
    parser.add_argument("--config", default=".clean_files", help="Path to config file (default: .clean_files)")
    parser.add_argument("--yes", action="store_true", help="Auto-confirm all prompts (Non-interactive)")

    args = parser.parse_args()
    
    
    if args.all:
        args.empty = args.temporary = args.sanitize = args.permissions = args.duplicates = True

    # Validate inputs
    if not args.target_dir:
        parser.print_help()
        sys.exit(1)

    print(f"{Colors.BOLD}Starting File Organizer...{Colors.ENDC}")
    
    # Initialize the Organizer Object
    organizer = FileOrganizer(args.target_dir, args.source_dirs, args.config, args.yes)
    
    # Execute Steps
    if args.empty: 
        organizer.remove_empty_and_temp()
    if args.temporary and not args.empty:
        organizer.remove_empty_and_temp()
        
    if args.sanitize: 
        organizer.sanitize_filenames()
        
    if args.permissions: 
        organizer.fix_permissions()
        
    if args.duplicates: 
        organizer.consolidate_and_dedup()
    
    if not any([args.empty, args.temporary, args.sanitize, args.permissions, args.duplicates]):
        print(f"{Colors.WARNING}No action selected. Use --all or specific flags like --duplicates.{Colors.ENDC}")
        print(f"Example: python3 file_organizer.py ./X ./Y --all")

if __name__ == "__main__":
    main()