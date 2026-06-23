from pathlib import Path
from src.core.cache_manager import CacheManager

def test_cache_manager_flow(tmp_path: Path) -> None:
    cm = CacheManager(cache_dir=tmp_path)
    
    # Cache should be empty initially
    assert cm.load_cache("test_cache") == {}
    
    # Save cache
    test_data = {"key": "value", "list": [1, 2, 3]}
    cm.save_cache("test_cache", test_data)
    
    # Load cache and verify structure
    loaded = cm.load_cache("test_cache")
    assert "_timestamp" in loaded
    assert loaded["data"] == test_data
    
    # Test expiry checks
    assert cm.is_expired("test_cache", days=7) is False
    assert cm.is_expired("test_cache", days=-1) is True # instantly expired
    
    # Clear cache
    cm.clear_cache("test_cache")
    assert cm.load_cache("test_cache") == {}
    assert cm.is_expired("test_cache") is True
