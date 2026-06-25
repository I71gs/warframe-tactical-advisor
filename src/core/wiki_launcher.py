from __future__ import annotations
import webbrowser
from urllib.parse import quote
from src.utils.logger import logger

class WikiLauncher:
    """Directly launches default OS web browsers to warframe.wiki.gg or fandom.com for queried items."""

    def __init__(self, use_wiki_gg: bool | None = None) -> None:
        if use_wiki_gg is not None:
            self.use_wiki_gg = use_wiki_gg
        else:
            try:
                from src.core.settings_manager import SettingsManager
                self.use_wiki_gg = SettingsManager().get('use_wiki_gg', True)
            except Exception:
                self.use_wiki_gg = True

    def get_url(self, item_name: str) -> str:
        safe_name = quote(item_name.replace(" ", "_"))
        if self.use_wiki_gg:
            return f"https://warframe.wiki.gg/wiki/{safe_name}"
        else:
            return f"https://warframe.fandom.com/wiki/{safe_name}"

    def launch_wiki(self, item_name: str) -> bool:
        url = self.get_url(item_name)
        try:
            webbrowser.open(url)
            logger.info("Launched web browser for: %s at %s", item_name, url)
            return True
        except Exception as e:
            logger.error("Failed to launch wiki page for %s: %s", item_name, e)
            return False
