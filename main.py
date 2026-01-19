import argparse
import hashlib
import os
import sys
import logging
import stat

from pathlib import Path
from pyparsing import List, Optional


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


    def _load_config(self, path: str) -> dict:
        """
        Loads configuration from a file. 
        Supports simple KEY="VALUE" format (Bash-style) to be compatible with legacy config files.
        """
        defaults = {
            'temp_ext': ['.tmp', '.bak', '.~', '.swp', '.ds_store', '.old'],
            'bad_chars': [':', '*', '?', '"', '<', '>', '|', '$', ' '],
            'replace_char': '_',
            'perms': 0o644
        }
        
        config_path = Path(path).expanduser()
        
        # Fallback: look in current directory if specific path not found
        if not config_path.exists():
            local_conf = Path.cwd() / ".clean_files"
            if local_conf.exists():
                config_path = local_conf

        if not config_path.exists():
            logger.warning(f"{Colors.WARNING}Config file not found. Using internal defaults.{Colors.ENDC}")
            return defaults

        logger.info(f"Loading config from: {config_path}")
        try:
            settings = defaults.copy()
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    
                    if '=' in line:
                        key, val = line.split('=', 1)
                        val = val.strip().strip('"\'')
                        
                        if key == 'TMP_FILES':
                            settings['temp_ext'] = [x.strip() for x in val.split(',')]
                        elif key == 'TRICKY_LETTERS':
                            settings['bad_chars'] = list(val.replace(' ', '')) 
                            if ' ' in val: settings['bad_chars'].append(' ')
                        elif key == 'TRICKY_LETTER_SUBSTITUTE':
                            settings['replace_char'] = val
                        elif key == 'SUGGESTED_ACCESS':
                            settings['perms'] = int(val, 8)
            return settings
        except Exception as e:
            logger.error(f"{Colors.FAIL}Config parsing error: {e}{Colors.ENDC}")
            return defaults
        
    def _ask_user(self, question: str) -> bool:
        """
        Handles interactive user prompts.
        Returns True for 'yes', False for 'no'.
        """
        if self.auto_mode:
            return True
        
        while True:
            response = input(f"{Colors.BLUE}{question} [y/n/all]: {Colors.ENDC}").lower().strip()
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            if response in ['a', 'all']:
                self.auto_mode = True
                print(f"{Colors.BOLD}Auto-mode enabled for remaining operations.{Colors.ENDC}")
                return True

    def _calculate_hash(self, filepath: Path) -> Optional[str]:
        """Calculates MD5 hash for content comparison. Optimized for large files."""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                # Read in 8KB chunks to avoid memory issues
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except OSError:
            return None


    def remove_empty_and_temp(self):
        """Scans for and removes empty files and files with temporary extensions."""
        print(f"\n{Colors.HEADER}=== Cleaning Junk Files ==={Colors.ENDC}")
        temp_exts = self.config['temp_ext']
        
        for directory in self.all_dirs:
            if not directory.exists(): continue
            
            for root, _, files in os.walk(directory):
                for file in files:
                    path = Path(root) / file
                    try:
                        # 1. Check Empty
                        if path.stat().st_size == 0:
                            if self._ask_user(f"Remove EMPTY file: {path.name}?"):
                                path.unlink()
                                print(f"{Colors.FAIL}Deleted empty: {path}{Colors.ENDC}")
                                continue
                        
                        # 2. Check Temp Extensions
                        if any(file.endswith(ext) for ext in temp_exts):
                            if self._ask_user(f"Remove TEMP file: {path.name}?"):
                                path.unlink()
                                print(f"{Colors.FAIL}Deleted temp: {path}{Colors.ENDC}")

                    except OSError as e:
                        logger.error(f"Error accessing {path}: {e}")

    def sanitize_filenames(self):
        pass

    def fix_permissions(self):
        """Resets file permissions to the default value (e.g., 644)."""
        print(f"\n{Colors.HEADER}=== Fixing Permissions ==={Colors.ENDC}")
        target_mode = self.config['perms']
        
        for directory in self.all_dirs:
            if not directory.exists(): continue
            for root, _, files in os.walk(directory):
                for file in files:
                    path = Path(root) / file
                    try:
                        # Get current permissions (masked to standard bits)
                        current = stat.S_IMODE(path.stat().st_mode)
                        if current != target_mode:
                            if self._ask_user(f"Fix permissions for {path.name} ({oct(current)} -> {oct(target_mode)})?"):
                                path.chmod(target_mode)
                                print(f"{Colors.GREEN}Fixed: {path.name}{Colors.ENDC}")
                    except OSError:
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