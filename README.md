# ASU directory-consolidator
A Python utility for cleaning, organizing, and consolidating file structures. This tool scans directories to identify and resolve common file issues such as duplicates, temporary files, naming conflicts, and permission errors.

## Features

This script performs the following cleaning actions based on user selection:

* **Consolidate & Deduplicate:** Merges files from Source Directories (`Y1`, `Y2`...) into a Target Directory (`X`).
    * *Content Duplicates:* Keeps the **OLDEST** file (Original) and removes newer copies.
    * *Name Conflicts:* If files have the same name but different content, keeps the **NEWEST** version.
* **Clean Junk:** Detects and removes empty files and files with temporary extensions (e.g., `.tmp`, `.bak`).
* **Sanitize Filenames:** Renames files containing "tricky" characters (like `:`, `*`, `?`, `$`) to a safe substitute (e.g., `_`).
* **Fix Permissions:** Resets file permissions to a safe default (e.g., `644` / `rw-r-r-`).

## Prerequisites

* **Python 3.6+** (Standard libraries only; no `pip install` required).
* **Linux/Unix** environment (Recommended for permission features).

## Configuration

The script looks for a configuration file to define rules. It searches in the following order:
1.  Path specified via `--config`.
2.  `.clean_files` in the current working directory.
3.  `$HOME/.clean_files`.

### Config File Format (`.clean_files`)
The file uses a simple `KEY="VALUE"` format.

**Important:** `TMP_FILES` should be a comma-separated list of extensions (note: the code logic uses `endswith`, not regex).

```bash
# Target permissions (Octal, usually 644 or 755)
SUGGESTED_ACCESS="644"

# Characters to remove from filenames
TRICKY_LETTERS=":\"';*?#|\\$ "

# Character to replace tricky letters with
TRICKY_LETTER_SUBSTITUTE="_"

# Comma-separated list of extensions to delete
TMP_FILES=".tmp, .bak, .swp, .~, .ds_store, .old"
```

## Usage

Run the script from the terminal. You must specify the **Target Directory (X)** first, followed by one or more **Source Directories (Y)**.

```bash
python3 main.py [TARGET_DIR] [SOURCE_DIRS...] [FLAGS]
```
### Options & Flags

| Flag | Description |
| :--- | :--- |
| **Directory Arguments** | |
| `TARGET_DIR` | The main catalog (e.g., `./X`) where files will be consolidated. |
| `SOURCE_DIRS` | One or more source catalogs (e.g., `./Y1 ./Y2`) to scan. |
| **Action Flags** | |
| `-d`, `--duplicates` | **Main Action:** Consolidate files to Target and remove duplicates. |
| `-e`, `--empty` | Remove empty files (0 bytes). |
| `-t`, `--temporary` | Remove temporary files based on config extensions. |
| `-s`, `--sanitize` | Rename files with special characters. |
| `-p`, `--permissions` | Fix file permissions. |
| `-a`, `--all` | **Run ALL above actions.** |
| **General Options** | |
| `--config FILE` | Path to a specific config file (default: `.clean_files`). |
| `--yes` | **Auto-Mode:** Answer "Yes" to all prompts automatically. |

### Examples

**1. Basic Cleanup (No Moving)**
Clean junk files (`.tmp`, empty) and fix permissions in folders `Y1` and `Y2`.
*Note: You must still provide a target directory argument, even if just cleaning sources.*
```bash
python3 main.py ./X ./Y1 ./Y2 -e -t -p
```

**2. Full Consolidation (The "Project Goal")**
Move files from `Y1`, `Y2`, `Y3` into `X`, handling duplicates and conflicts automatically:
```bash
python3 main.py ./X ./Y1 ./Y2 ./Y3 --duplicates --yes
```

**3. Run Everything**
Perform all cleanup tasks, sanitize names, and consolidate:
```bash
python3 main.py ./X ./Y1 ./Y2 -a
```

## Testing

A test generator script is included to create a messy environment with duplicates, conflicts, and bad permissions.

1.  Generate the test files:
    ```bash
    python3 generator.py
    ```
2.  Run the organizer:
    ```bash
    python3 main.py ./X ./Y1 ./Y2 ./Y3 --all
    ```