from __future__ import annotations
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Any
from src.utils.logger import logger

ROOT = Path(__file__).resolve().parents[2]
PROFILES_DIR = ROOT / "profiles"

class SaveManager:
    """Manages multi-save profile folders, auto backup rotations, and restore points."""

    def __init__(self, profiles_dir: Path | str | None = None) -> None:
        self.profiles_dir = Path(profiles_dir) if profiles_dir else PROFILES_DIR
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.migrate_legacy_db()

    def migrate_legacy_db(self) -> None:
        """Migrates player.db from legacy root paths into the profiles folder."""
        legacy_db = ROOT / "player.db"
        default_profile_db = self.profiles_dir / "default" / "player.db"
        if legacy_db.exists() and not default_profile_db.exists():
            default_profile_db.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(legacy_db, default_profile_db)
                logger.info("Migrated legacy root player.db to profiles/default/player.db")
            except Exception as e:
                logger.error("Failed to migrate legacy db: %s", e)

    def list_profiles(self) -> list[str]:
        """Returns directories under profiles/ containing database configurations."""
        if not self.profiles_dir.exists():
            return ["default"]
        profiles = [p.name for p in self.profiles_dir.iterdir() if p.is_dir()]
        if not profiles:
            return ["default"]
        return sorted(profiles)

    def get_profile_db_path(self, name: str) -> Path:
        """Returns path to player.db for the requested profile name."""
        return self.profiles_dir / name / "player.db"

    def create_profile(self, name: str) -> Path:
        """Initializes directory structure for a new profile."""
        profile_path = self.profiles_dir / name
        profile_path.mkdir(parents=True, exist_ok=True)
        db_path = profile_path / "player.db"
        
        # If it doesn't exist, create it by importing DatabaseManager to create tables
        if not db_path.exists():
            from src.database.database import DatabaseManager
            db = DatabaseManager(db_path=db_path)
            db.connection.close()
            logger.info("Created new profile db: %s", name)
        return db_path

    def delete_profile(self, name: str) -> None:
        profile_path = self.profiles_dir / name
        if profile_path.exists() and name != "default":
            try:
                shutil.rmtree(profile_path)
                logger.info("Deleted profile: %s", name)
            except Exception as e:
                logger.error("Failed to delete profile %s: %s", name, e)

    def create_restore_point(self, profile_name: str, label: str) -> Path | None:
        """Creates a snapshot restore point inside the profile's restore_points folder."""
        db_path = self.get_profile_db_path(profile_name)
        if not db_path.exists():
            return None
        
        restore_dir = self.profiles_dir / profile_name / "restore_points"
        restore_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_label = "".join(c for c in label if c.isalnum() or c in ("-", "_")).strip()
        filename = f"{safe_label}_{timestamp}.sqlite"
        dest_path = restore_dir / filename
        
        try:
            shutil.copy2(db_path, dest_path)
            logger.info("Created restore point %s for profile %s", filename, profile_name)
            return dest_path
        except Exception as e:
            logger.error("Failed to create restore point: %s", e)
            return None

    def list_restore_points(self, profile_name: str) -> list[dict[str, Any]]:
        restore_dir = self.profiles_dir / profile_name / "restore_points"
        if not restore_dir.exists():
            return []
        
        points = []
        for f in restore_dir.glob("*.sqlite"):
            points.append({
                "filename": f.name,
                "path": str(f),
                "timestamp": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
        return sorted(points, key=lambda x: x["filename"], reverse=True)

    def restore_to_point(self, profile_name: str, filename: str) -> bool:
        src_path = self.profiles_dir / profile_name / "restore_points" / filename
        dest_path = self.get_profile_db_path(profile_name)
        if not src_path.exists():
            return False
        try:
            # Create a backup of the current database before restoring
            self.rotate_auto_backups(profile_name)
            shutil.copy2(src_path, dest_path)
            logger.info("Restored profile %s database to point: %s", profile_name, filename)
            return True
        except Exception as e:
            logger.error("Failed to restore profile database: %s", e)
            return False

    def rotate_auto_backups(self, profile_name: str, max_backups: int = 5) -> Path | None:
        """Saves current db to backups/ folder and deletes oldest backup files keeping up to max_backups."""
        db_path = self.get_profile_db_path(profile_name)
        if not db_path.exists():
            return None
        
        backup_dir = self.profiles_dir / profile_name / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_path = backup_dir / f"auto_{timestamp}.sqlite"
        
        try:
            shutil.copy2(db_path, dest_path)
            
            # Clean up old backups
            backups = sorted(list(backup_dir.glob("auto_*.sqlite")), key=lambda x: x.name)
            if len(backups) > max_backups:
                to_delete = backups[:len(backups) - max_backups]
                for old in to_delete:
                    old.unlink()
                    logger.info("Cleaned up old auto backup: %s", old.name)
                    
            return dest_path
        except Exception as e:
            logger.error("Failed to rotate backups: %s", e)
            return None
