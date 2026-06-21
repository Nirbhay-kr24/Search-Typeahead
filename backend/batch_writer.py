from collections import defaultdict
import threading
import time

from sqlalchemy import text

search_buffer = defaultdict(int)


def start_batch_writer(engine):

    def flush():

        while True:

            time.sleep(10)

            if not search_buffer:
                continue

            print(
                f"FLUSHING {dict(search_buffer)}"
            )

            with engine.connect() as conn:

                for query, count in list(
                    search_buffer.items()
                ):

                    existing = conn.execute(
                        text("""
                        SELECT query
                        FROM queries
                        WHERE query=:query
                        """),
                        {"query": query}
                    ).fetchone()

                    if existing:

                        conn.execute(
                            text("""
                            UPDATE queries
                            SET count = count + :count,
                                recent_score = recent_score + :recent_score,
                                updated_at = NOW()
                            WHERE query=:query
                            """),
                            {
                                "query": query,
                                "count": count,
                                "recent_score": count * 5000
                            }
                        )

                    else:

                        conn.execute(
                            text("""
                            INSERT INTO queries
                            (
                                query,
                                count,
                                recent_score
                            )
                            VALUES
                            (
                                :query,
                                :count,
                                :recent_score
                            )
                            """),
                            {
                                "query": query,
                                "count": count,
                                "recent_score": count * 5000
                            }
                        )

                conn.commit()

            search_buffer.clear()

    threading.Thread(
        target=flush,
        daemon=True
    ).start()


def start_decay_worker(engine):

    def decay():

        while True:

            time.sleep(60)

            with engine.connect() as conn:

                conn.execute(
                    text("""
                    UPDATE queries
                    SET recent_score =
                        recent_score * 0.95
                    """)
                )

                conn.commit()

                print(
                    "RECENCY DECAY APPLIED"
                )

    threading.Thread(
        target=decay,
        daemon=True
    ).start()


    