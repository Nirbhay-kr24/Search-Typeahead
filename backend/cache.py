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

        print(
            f"CACHE HIT -> {key} on {node}"
        )

        return (
            json.loads(value),
            node,
            True
        )

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
    