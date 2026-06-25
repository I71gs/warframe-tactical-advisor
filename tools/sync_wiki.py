from __future__ import annotations
import json
import urllib.request
import urllib.parse
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils.logger import logger

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "src" / "resources" / "data"

WEAPONS_JSON_PATH = DATA_DIR / "weapons.json"
MODS_JSON_PATH = DATA_DIR / "mods.json"
ARCANES_JSON_PATH = DATA_DIR / "arcanes.json"
WARFRAMES_JSON_PATH = DATA_DIR / "warframes.json"
COMPANIONS_JSON_PATH = DATA_DIR / "companions.json"
QUESTS_JSON_PATH = DATA_DIR / "quests.json"

FANDOM_API_URL = "https://warframe.fandom.com/api.php"
HEADERS = {"User-Agent": "WarframeTacticalAdvisorSync/1.0 (contact: admin@wta.local)"}

def fetch_wiki_page_content(title: str) -> str:
    """Fetch raw page content via MediaWiki revisions API."""
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvslots": "*",
        "rvprop": "content",
        "format": "json"
    }
    url = FANDOM_API_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for _, page_data in pages.items():
                return page_data.get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("*", "")
    except Exception as e:
        logger.error("Wiki Sync: Failed to fetch page content for %s: %s", title, e)
    return ""

def fetch_wiki_parsed_html(title: str) -> str:
    """Fetch parsed HTML text for a page to scrape source/description context."""
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json"
    }
    url = FANDOM_API_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("parse", {}).get("text", {}).get("*", "")
    except Exception as e:
        logger.error("Wiki Sync: Failed to fetch parsed page HTML for %s: %s", title, e)
    return ""

def determine_source_from_html(html: str, default_source: str) -> str:
    """Heuristically identify acquisition source based on keywords in parsed page HTML."""
    # Slice HTML to focus on introduction and infobox, avoiding footer navboxes
    html_slice = html[:100000].lower()
    
    if "bio lab" in html_slice or "clan dojo" in html_slice:
        return "Clan Dojo (Bio Lab)"
    if "cavalero" in html_slice or "holdfast" in html_slice:
        return "Cavalero Vendor (Zariman)"
    if "acolyte" in html_slice:
        return "Steel Path Acolytes"
    if "eidolon" in html_slice or "quill" in html_slice:
        return "Eidolons"
    if "arbitration" in html_slice:
        return "Arbitrations"
    if "steel path" in html_slice:
        return "Steel Path Acolytes"
    if "baro ki'teer" in html_slice or "void trader" in html_slice:
        return "Baro Ki'Teer"
    if "syndicate" in html_slice or "arbiters of hexis" in html_slice:
        return "Syndicate Vendor"
    if "chem lab" in html_slice:
        return "Clan Dojo (Chem Lab)"
    if "tenno lab" in html_slice:
        return "Clan Dojo (Tenno Lab)"
    if "nakak" in html_slice:
        return "Nakak (Cetus)"
    if "yonta" in html_slice:
        return "Archimedean Yonta (Zariman)"
    
    return default_source

def sync_weapons() -> int:
    """Sync weapons.json with Module:Weapons/data on the wiki."""
    if not WEAPONS_JSON_PATH.exists():
        return 0
        
    logger.info("Wiki Sync: Syncing weapons.json...")
    with open(WEAPONS_JSON_PATH, "r", encoding="utf-8") as f:
        weapons = json.load(f)
        
    # Fetch primary, secondary, and melee Lua modules to search within them
    modules = [
        "Module:Weapons/data/primary",
        "Module:Weapons/data/secondary",
        "Module:Weapons/data/melee"
    ]
    lua_data = ""
    for m in modules:
        lua_data += fetch_wiki_page_content(m) + "\n"
        
    updated_count = 0
    for w in weapons:
        name = w.get("name")
        if not name:
            continue
            
        # Extract block for the weapon name in Lua
        pattern = rf"\b{re.escape(name)}\s*=\s*\{{.*?\n\s*\}}[,]?"
        match = re.search(pattern, lua_data, re.DOTALL)
        if match:
            block = match.group(0)
            
            # Parse stats
            mr_match = re.search(r"Mastery\s*=\s*(\d+)", block)
            slot_match = re.search(r"Slot\s*=\s*\"([^\"]+)\"", block)
            class_match = re.search(r"Class\s*=\s*\"([^\"]+)\"", block)
            
            if mr_match:
                w["mastery_required"] = int(mr_match.group(1))
            if slot_match:
                w["type"] = slot_match.group(1)
            if class_match:
                w["category"] = class_match.group(1)
                
            # Parse parsed page HTML for acquisition source
            html = fetch_wiki_parsed_html(name)
            w["acquisition"] = determine_source_from_html(html, w.get("acquisition", "Wiki Query"))
            updated_count += 1
            
    with open(WEAPONS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(weapons, f, indent=4)
        
    logger.info("Wiki Sync: Successfully updated %d weapons.", updated_count)
    return updated_count

def sync_mods() -> int:
    """Sync mods.json with Module:Mods/data on the wiki."""
    if not MODS_JSON_PATH.exists():
        return 0
        
    logger.info("Wiki Sync: Syncing mods.json...")
    with open(MODS_JSON_PATH, "r", encoding="utf-8") as f:
        mods = json.load(f)
        
    # Fetch Module:Mods/data content
    lua_data = fetch_wiki_page_content("Module:Mods/data")
    
    updated_count = 0
    for m in mods:
        name = m.get("name")
        if not name:
            continue
            
        # Extract block for mod name in Lua
        pattern = rf'\["{re.escape(name)}"\]\s*=\s*\{{.*?\n\s*\}}[,]?'
        match = re.search(pattern, lua_data, re.DOTALL)
        if match:
            block = match.group(0)
            
            # Parse stats
            class_match = re.search(r"Class\s*=\s*\"([^\"]+)\"", block)
            type_match = re.search(r"Type\s*=\s*\"([^\"]+)\"", block)
            
            if class_match:
                m["class"] = class_match.group(1)
            if type_match:
                m["category"] = type_match.group(1) + " Mod"
                
            # Parse parsed page HTML for acquisition source
            html = fetch_wiki_parsed_html(name)
            m["source"] = determine_source_from_html(html, m.get("source", "Wiki Query"))
            updated_count += 1
            
    with open(MODS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(mods, f, indent=4)
        
    logger.info("Wiki Sync: Successfully updated %d mods.", updated_count)
    return updated_count

def sync_arcanes() -> int:
    """Sync arcanes.json by pulling info directly from Fandom pages."""
    if not ARCANES_JSON_PATH.exists():
        return 0
        
    logger.info("Wiki Sync: Syncing arcanes.json...")
    with open(ARCANES_JSON_PATH, "r", encoding="utf-8") as f:
        arcanes = json.load(f)
        
    updated_count = 0
    for a in arcanes:
        name = a.get("name")
        if not name:
            continue
            
        html = fetch_wiki_parsed_html(name)
        a["source"] = determine_source_from_html(html, a.get("source", "Wiki Query"))
        updated_count += 1
        
    with open(ARCANES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(arcanes, f, indent=4)
        
    logger.info("Wiki Sync: Successfully updated %d arcanes.", updated_count)
    return updated_count

def sync_warframes() -> int:
    """Sync warframes.json with Module:Warframes/data on the wiki."""
    if not WARFRAMES_JSON_PATH.exists():
        return 0
        
    logger.info("Wiki Sync: Syncing warframes.json...")
    with open(WARFRAMES_JSON_PATH, "r", encoding="utf-8") as f:
        warframes = json.load(f)
        
    lua_data = fetch_wiki_page_content("Module:Warframes/data")
    
    updated_count = 0
    for w in warframes:
        name = w.get("name")
        if not name:
            continue
            
        # Parse stats from Module:Warframes/data
        pattern = rf"\b{re.escape(name)}\s*=\s*\{{.*?\n\s*\}}[,]?"
        match = re.search(pattern, lua_data, re.DOTALL)
        if match:
            block = match.group(0)
            
            # Abilities array
            abilities_match = re.search(r"Abilities\s*=\s*\{([^\}]+)\}", block)
            if abilities_match:
                abilities_str = abilities_match.group(1)
                abilities = [a.strip().strip('"').strip("'") for a in abilities_str.split(",")]
                w["abilities"] = [a for a in abilities if a]
                
            # Passive
            passive_match = re.search(r"Passive\s*=\s*\"([^\"]+)\"", block)
            if passive_match:
                w["passive"] = passive_match.group(1)
                
            # Subsumed
            subsumed_match = re.search(r"Subsumed\s*=\s*\"([^\"]+)\"", block)
            if subsumed_match:
                w["subsumed"] = subsumed_match.group(1)
                w["helminth"] = subsumed_match.group(1)
                
            # Description
            desc_match = re.search(r"Description\s*=\s*\"([^\"]+)\"", block)
            if desc_match:
                w["description"] = desc_match.group(1)
                
        # Parse parsed page HTML for acquisition source
        html = fetch_wiki_parsed_html(name)
        w["acquisition"] = determine_source_from_html(html, w.get("acquisition", "Wiki Query"))
        updated_count += 1
        
    with open(WARFRAMES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(warframes, f, indent=4)
        
    logger.info("Wiki Sync: Successfully updated %d warframes.", updated_count)
    return updated_count

def sync_companions() -> int:
    """Sync companions.json with Module:Companions/data on the wiki."""
    if not COMPANIONS_JSON_PATH.exists():
        return 0
        
    logger.info("Wiki Sync: Syncing companions.json...")
    with open(COMPANIONS_JSON_PATH, "r", encoding="utf-8") as f:
        companions = json.load(f)
        
    lua_data = fetch_wiki_page_content("Module:Companions/data")
    
    updated_count = 0
    for c in companions:
        name = c.get("name")
        if not name:
            continue
            
        # Parse block from Module:Companions/data
        pattern = rf'(?:\["{re.escape(name)}"\]|\b{re.escape(name)})\s*=\s*\{{.*?\n\s*\}}[,]?'
        match = re.search(pattern, lua_data, re.DOTALL)
        if match:
            block = match.group(0)
            
            # Type
            type_match = re.search(r"Type\s*=\s*\"([^\"]+)\"", block)
            if type_match:
                c["type"] = type_match.group(1)
                
            # Description
            desc_match = re.search(r"Description\s*=\s*\"([^\"]+)\"", block)
            if desc_match:
                c["description"] = desc_match.group(1)
                
        # Parse parsed page HTML for acquisition source
        html = fetch_wiki_parsed_html(name)
        c["acquisition"] = determine_source_from_html(html, c.get("acquisition", "Wiki Query"))
        updated_count += 1
        
    with open(COMPANIONS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(companions, f, indent=4)
        
    logger.info("Wiki Sync: Successfully updated %d companions.", updated_count)
    return updated_count

def sync_quests() -> int:
    """Sync quests.json by pulling info from Fandom pages."""
    if not QUESTS_JSON_PATH.exists():
        return 0
        
    logger.info("Wiki Sync: Syncing quests.json...")
    with open(QUESTS_JSON_PATH, "r", encoding="utf-8") as f:
        quests = json.load(f)
        
    updated_count = 0
    for q in quests:
        name = q.get("name")
        if not name:
            continue
            
        html = fetch_wiki_parsed_html(name)
        html_slice = html[:100000].lower()
        
        # Scrape acquisition context from page HTML (e.g. from Teshin, inbox, etc.)
        if "inbox" in html_slice:
            q["acquisition"] = "Inbox Message"
        elif "teshin" in html_slice:
            q["acquisition"] = "Teshin (Relay)"
        elif "darvo" in html_slice:
            q["acquisition"] = "Darvo (Cetus/Relay)"
        elif "konzu" in html_slice:
            q["acquisition"] = "Konzu (Cetus)"
        else:
            q["acquisition"] = q.get("acquisition") or "Quest Log / Codex"
            
        # Extract brief description using simple text scan
        desc_match = re.search(r"<p>.*?<b>" + re.escape(name) + r"</b>.*?(.*?)</p>", html, re.IGNORECASE)
        if desc_match:
            clean_desc = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()
            q["description"] = clean_desc[:200]
            
        updated_count += 1
        
    with open(QUESTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(quests, f, indent=4)
        
    logger.info("Wiki Sync: Successfully updated %d quests.", updated_count)
    return updated_count

def sync_all_wiki() -> dict[str, int]:
    """Runs synchronization on all dataset files."""
    results = {
        "weapons": sync_weapons(),
        "mods": sync_mods(),
        "arcanes": sync_arcanes(),
        "warframes": sync_warframes(),
        "companions": sync_companions(),
        "quests": sync_quests()
    }
    return results

if __name__ == "__main__":
    import sys
    print("Starting Warframe Wiki Database Synchronization...")
    try:
        res = sync_all_wiki()
        print("Synchronization completed successfully!")
        print(f"Updated: {res['weapons']} weapons, {res['mods']} mods, {res['arcanes']} arcanes,")
        print(f"         {res['warframes']} warframes, {res['companions']} companions, {res['quests']} quests.")
    except Exception as exc:
        print(f"Error during synchronization: {exc}")
        sys.exit(1)
