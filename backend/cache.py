import redis
import hashlib
import json

CACHE_TTL = 60

cache_nodes = {
    "node1": redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True
    ),

    "node2": redis.Redis(
        host="localhost",
        port=6380,
        decode_responses=True
    ),

    "node3": redis.Redis(
        host="localhost",
        port=6381,
        decode_responses=True
    )
}

# Cache statistics tracking
cache_stats = {
    "node1": {
        "hits": 0,
        "misses": 0
    },
    "node2": {
        "hits": 0,
        "misses": 0
    },
    "node3": {
        "hits": 0,
        "misses": 0
    }
}


def get_node(key):

    h = int(
        hashlib.md5(
            key.encode()
        ).hexdigest(),
        16
    )

    nodes = list(
        cache_nodes.keys()
    )

    return nodes[
        h % len(nodes)
    ]


def get_cache(key):

    node = get_node(key)

    value = cache_nodes[node].get(key)

    if value:

        cache_stats[node]["hits"] += 1

        print(
            f"CACHE HIT -> {key} on {node}"
        )

        return (
            json.loads(value),
            node,
            True
        )

    cache_stats[node]["misses"] += 1

    print(
        f"CACHE MISS -> {key} on {node}"
    )

    return None,node,False


def set_cache(
    key,
    value
):

    node = get_node(key)

    cache_nodes[node].setex(
        key,
        CACHE_TTL,
        json.dumps(value)
    )

    print(
        f"SET CACHE -> {key} on {node}"
    )


def invalidate_prefix(
    prefix
):

    node = get_node(prefix)

    cache_nodes[node].delete(
        prefix
    )

    print(
        f"INVALIDATED -> {prefix} on {node}"
    )


def get_cache_stats():
    """Get cache hit/miss statistics"""
    
    stats = {}
    total_hits = 0
    total_misses = 0
    
    for node, data in cache_stats.items():
        hits = data["hits"]
        misses = data["misses"]
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        stats[node] = {
            "hits": hits,
            "misses": misses,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2)
        }
        
        total_hits += hits
        total_misses += misses
    
    # Calculate overall hit rate
    total_requests = total_hits + total_misses
    overall_hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
    
    return {
        "by_node": stats,
        "overall": {
            "hits": total_hits,
            "misses": total_misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(overall_hit_rate, 2)
        }
    }


def reset_cache_stats():
    """Reset cache statistics"""
    
    for node in cache_stats:
        cache_stats[node]["hits"] = 0
        cache_stats[node]["misses"] = 0
    
    print("Cache statistics reset")
