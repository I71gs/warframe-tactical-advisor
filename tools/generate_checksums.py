from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"

def calculate_sha256(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read file in chunks to handle large binaries
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main() -> None:
    print("========================================================")
    print("SHA256 Hash Checksum Generator")
    print("========================================================")
    
    if not DIST_DIR.exists():
        print(f"Error: Release folder '{DIST_DIR}' does not exist. Build the app first!")
        return
        
    hash_lines = []
    # Search for compiled binaries and zip archives
    extensions = ("*.exe", "*.zip", "*.msi")
    found_files = []
    for ext in extensions:
        found_files.extend(list(DIST_DIR.glob(ext)))
        found_files.extend(list(DIST_DIR.glob(f"**/{ext}")))
        
    # De-duplicate files
    unique_files = list(set(found_files))
    
    if not unique_files:
        print("No compiled release files (.exe, .zip, .msi) found in 'dist/'.")
        return
        
    print(f"Found {len(unique_files)} files. Calculating hashes...")
    for filepath in sorted(unique_files):
        # Calculate hash
        sha256 = calculate_sha256(filepath)
        filename = filepath.name
        line = f"{sha256}  {filename}"
        hash_lines.append(line)
        print(line)
        
    # Save hashes to dist/SHA256.txt
    output_path = DIST_DIR / "SHA256.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(hash_lines) + "\n")
        
    print("--------------------------------------------------------")
    print(f"Hashes successfully saved to: {output_path}")
    print("========================================================")

if __name__ == "__main__":
    main()
