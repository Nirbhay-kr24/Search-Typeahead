import time

from fastapi import FastAPI

from sqlalchemy import create_engine,text

from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from cache import cache_nodes

from cache import (
    get_cache,
    set_cache,
    invalidate_prefix,
    get_cache_stats,
    reset_cache_stats
)


from batch_writer import (
    search_buffer,
    start_batch_writer,
    start_decay_worker
)


class SearchRequest(BaseModel):
    query: str

DATABASE_URL = (
    "postgresql://admin:admin@localhost:5432/searchdb"
)

engine = create_engine(DATABASE_URL)

start_batch_writer(engine)

start_decay_worker(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {
        "message":"Search Typeahead Running"
    }


import time


@app.get("/suggest")
def suggest(q: str = ""):

    start = time.perf_counter()

    if not q.strip():
        return {
            "results": [],
            "latency_ms": 0,
            "source": "none"
        }

    # Check Redis Cache
    cached, node, hit = get_cache(q)

    if hit:

        latency = round(
            (time.perf_counter() - start) * 1000,
            2
        )

        print(
            f"CACHE HIT: {latency} ms"
        )

        return {
            "results": cached,
            "latency_ms": latency,
            "source": "redis"
        }

    # PostgreSQL Query
    sql = """
    SELECT query, count
    FROM queries
    WHERE LOWER(query)
    LIKE LOWER(:prefix)
    ORDER BY
        (count + recent_score) DESC
    LIMIT 10
    """

    with engine.connect() as conn:

        rows = conn.execute(
            text(sql),
            {
                "prefix": f"{q}%"
            }
        ).fetchall()

    result = [
        {
            "query": row[0],
            "count": row[1]
        }
        for row in rows
    ]

    # Store in Redis
    set_cache(
        q,
        result
    )

    latency = round(
        (time.perf_counter() - start) * 1000,
        2
    )

    print(
        f"DB HIT: {latency} ms"
    )

    return {
        "results": result,
        "latency_ms": latency,
        "source": "postgres"
    }


@app.post("/search")
def search(data: SearchRequest):

    query = data.query.strip().lower()

    if not query:
        return {
            "message":"Empty query"
        }

    search_buffer[query] += 1

    invalidate_prefix(
        query[:3]
    )

    return {
        "message":"Searched"
    }

    


@app.get("/trending")
def trending():

    sql = """
SELECT
    query,
    count,
    recent_score,
    (count + recent_score) as score

FROM queries

ORDER BY score DESC

LIMIT 10
"""

    with engine.connect() as conn:

        rows = conn.execute(
            text(sql)
        ).fetchall()

    return [
    {
        "query": row[0],
        "count": row[1],
        "recent_score": row[2],
        "score": row[3]
    }
    for row in rows
]


@app.get("/cache/debug")
def cache_debug(prefix:str):

    cached,node,hit = get_cache(prefix)

    return {
        "prefix": prefix,
        "node": node,
        "hit": hit,
        "cached_entries":
            cache_nodes[node].dbsize()
    }

@app.get("/stats")
def stats():

    cache_stats = get_cache_stats()

    return {

        "buffer_size":
            len(search_buffer),

        "cache_nodes": {

            node:
            cache.dbsize()

            for node,cache
            in cache_nodes.items()
        },

        "cache_performance": cache_stats
    }


@app.post("/stats/reset")
def reset_stats():

    reset_cache_stats()

    return {
        "message": "Cache statistics reset successfully"
    }