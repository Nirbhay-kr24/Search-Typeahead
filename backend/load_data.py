import pandas as pd  # type: ignore[import]
from sqlalchemy import create_engine,text

DATABASE_URL = (
    "postgresql://admin:admin@localhost:5432/searchdb"
)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text("DELETE FROM queries"))
    conn.commit()

df = pd.read_csv("../dataset/queries.csv")

df.to_sql(
    "queries",
    engine,
    if_exists="append",
    index=False
)

print(f"Loaded {len(df)} rows")