from __future__ import annotations
import json
import importlib.util
from pathlib import Path
from typing import Any, Callable
from src.core.weapon_database import WEAPONS
from src.core.build_database import BUILDS
from src.core.farming_database import FARMING_DATA
from src.utils.logger import logger

APP_VERSION = "7.0.0"

class PluginRegistry:
    """Singleton registry holding references to dynamically registered items, plugin manifests, and script extensions."""
    _instance: PluginRegistry | None = None

    def __new__(cls) -> PluginRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.weapons = []
            cls._instance.builds = []
            cls._instance.farming = {}
            cls._instance.commands = []
            cls._instance.tabs = []
            cls._instance.loaded_manifests = []
            cls._instance.routes = []
            cls._instance.themes = {}
        return cls._instance

    def register_weapon(self, weapon_data: dict[str, Any]) -> None:
        """Register a custom weapon and inject it dynamically into the active weapon list."""
        name = weapon_data.get("name")
        if not name:
            return
        self.weapons.append(weapon_data)
        if not any(w["name"].lower() == name.lower() for w in WEAPONS):
            WEAPONS.append(weapon_data)

    def register_build(self, build_data: dict[str, Any]) -> None:
        """Register a custom build and inject it dynamically into the active build database."""
        weapon = build_data.get("weapon")
        if not weapon:
            return
        self.builds.append(build_data)
        if not any(b["weapon"].lower() == weapon.lower() for b in BUILDS):
            BUILDS.append(build_data)

    def register_farming(self, weapon_name: str, farm_data: dict[str, Any]) -> None:
        """Register custom farming route and inject it dynamically into the farming dataset."""
        key = weapon_name.strip().lower()
        self.farming[key] = farm_data
        FARMING_DATA[key] = farm_data

    def register_command(self, label: str, callback: Callable[[], None]) -> None:
        """Register a custom palette command."""
        self.commands.append({"label": label, "action": callback})

    def register_tab(self, tab_class: type, title: str) -> None:
        """Register a custom GUI tab extension."""
        self.tabs.append({"class": tab_class, "title": title})

    def register_route(self, route_data: dict[str, Any]) -> None:
        """Register a custom farming route."""
        self.routes.append(route_data)

    def register_theme(self, name: str, theme_colors: dict[str, str]) -> None:
        """Register a custom theme from a plugin."""
        self.themes[name] = theme_colors

    def load_plugin_from_directory(self, plugin_dir: Path) -> bool:
        """Loads a plugin folder using the marketplace manifest convention."""
        manifest_path = plugin_dir / "manifest.json"
        if not manifest_path.exists():
            return False
            
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                
            # Compatibility checks
            min_ver = manifest.get("minimum_wta_version") or manifest.get("min_app_version") or "1.0.0"
            if not self.is_compatible(min_ver):
                logger.warning(
                    "Skipping plugin %s: Requires app version %s, current is %s",
                    manifest.get("name"), min_ver, APP_VERSION
                )
                return False
                
            # Verify dependencies
            deps = manifest.get("dependencies", [])
            for dep in deps:
                if not any(m.get("id") == dep for m in self.loaded_manifests):
                    logger.warning("Plugin dependency %s for %s not satisfied yet.", dep, manifest.get("name"))
            
            # Load weapons if exist
            weapons_file = plugin_dir / "weapons.json"
            if weapons_file.exists():
                with open(weapons_file, 'r', encoding='utf-8') as wf:
                    wdata = json.load(wf)
                    if isinstance(wdata, list):
                        for w in wdata:
                            self.register_weapon(w)
                            
            # Load builds if exist
            builds_file = plugin_dir / "builds.json"
            if builds_file.exists():
                with open(builds_file, 'r', encoding='utf-8') as bf:
                    bdata = json.load(bf)
                    if isinstance(bdata, list):
                        for b in bdata:
                            self.register_build(b)

            # Load routes if exist
            routes_file = plugin_dir / "routes.json"
            if routes_file.exists():
                with open(routes_file, 'r', encoding='utf-8') as rf:
                    rdata = json.load(rf)
                    if isinstance(rdata, list):
                        for r in rdata:
                            self.register_route(r)
                            target_name = r.get("weapon") or r.get("item")
                            if target_name:
                                self.register_farming(target_name, r)

            # Load theme if exist
            theme_file = plugin_dir / "theme.json"
            if theme_file.exists():
                with open(theme_file, 'r', encoding='utf-8') as tf:
                    tdata = json.load(tf)
                    if isinstance(tdata, dict) and "PRIMARY" in tdata:
                        tname = tdata.get("name") or plugin_dir.name.capitalize()
                        self.register_theme(tname, tdata)
                            
            # Load python commands script if exists
            commands_script = plugin_dir / "commands.py"
            if commands_script.exists():
                self._load_script(commands_script)
                
            self.loaded_manifests.append(manifest)
            logger.info("Successfully loaded plugin folder: %s", manifest.get("name"))
            return True
            
        except Exception as exc:
            logger.error("Failed to load plugin directory %s: %s", plugin_dir.name, exc)
            return False

    def is_compatible(self, required_version: str) -> bool:
        """Simple version comparison checks."""
        try:
            req_parts = [int(p) for p in required_version.split(".")]
            app_parts = [int(p) for p in APP_VERSION.split(".")]
            return app_parts >= req_parts
        except ValueError:
            return True

    def _load_script(self, script_path: Path) -> None:
        """Executes a Python commands.py file to allow dynamic callbacks."""
        try:
            spec = importlib.util.spec_from_file_location("plugin_commands", script_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # If module has 'register_plugin' method, call it passing self
                if hasattr(module, "register_plugin"):
                    module.register_plugin(self)
        except Exception as exc:
            logger.error("Failed executing plugin script %s: %s", script_path.name, exc)

    def clear(self) -> None:
        """Clear all registered items (useful for tests)."""
        self.weapons.clear()
        self.builds.clear()
        self.farming.clear()
        self.commands.clear()
        self.tabs.clear()
        self.loaded_manifests.clear()
