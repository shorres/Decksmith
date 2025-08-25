"""
Cache Management Utility for Magic Tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.persistent_cache import get_cache
import argparse

def show_cache_stats():
    """Show current cache statistics"""
    cache = get_cache()
    stats = cache.get_cache_stats()
    
    print("MAGIC TOOL CACHE STATISTICS")
    print("=" * 50)
    
    total_entries = 0
    total_valid = 0
    total_expired = 0
    
    for cache_type, data in stats.items():
        print(f"\n{cache_type.upper().replace('_', ' ')} CACHE:")
        print(f"  Total Entries: {data['total_entries']}")
        print(f"  Valid Entries: {data['valid_entries']}")
        print(f"  Expired Entries: {data['expired_entries']}")
        print(f"  Cache Duration: {data['expiry_hours']} hours")
        
        total_entries += data['total_entries']
        total_valid += data['valid_entries']
        total_expired += data['expired_entries']
    
    print(f"\nOVERALL SUMMARY:")
    print(f"  Total Cached Items: {total_entries}")
    print(f"  Valid Items: {total_valid}")
    print(f"  Expired Items: {total_expired}")
    
    if total_entries > 0:
        efficiency = (total_valid / total_entries) * 100
        print(f"  Cache Efficiency: {efficiency:.1f}%")

def cleanup_cache():
    """Clean up expired cache entries"""
    cache = get_cache()
    
    print("CLEANING UP EXPIRED CACHE ENTRIES")
    print("=" * 50)
    
    cleanup_stats = cache.cleanup_expired_entries()
    
    total_cleaned = sum(cleanup_stats.values())
    
    if total_cleaned > 0:
        print(f"Cleaned up {total_cleaned} expired entries:")
        for cache_type, count in cleanup_stats.items():
            if count > 0:
                print(f"  {cache_type}: {count} entries removed")
    else:
        print("No expired entries found - cache is clean!")

def clear_all_cache():
    """Clear all cache data"""
    cache = get_cache()
    
    print("CLEARING ALL CACHE DATA")
    print("=" * 50)
    
    confirm = input("Are you sure you want to clear ALL cached data? This will force fresh API calls. (y/N): ")
    
    if confirm.lower() == 'y':
        cache.clear_all_caches()
        print("✓ All cache data has been cleared")
    else:
        print("Cache clear cancelled")

def main():
    parser = argparse.ArgumentParser(description="Magic Tool Cache Management")
    parser.add_argument('action', choices=['stats', 'cleanup', 'clear'], 
                       help='Action to perform: stats (show statistics), cleanup (remove expired), clear (remove all)')
    
    args = parser.parse_args()
    
    if args.action == 'stats':
        show_cache_stats()
    elif args.action == 'cleanup':
        cleanup_cache()
    elif args.action == 'clear':
        clear_all_cache()

if __name__ == "__main__":
    main()
