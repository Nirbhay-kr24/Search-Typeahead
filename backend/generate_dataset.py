import pandas as pd
import random

queries = [
    "iphone",
    "iphone 15",
    "iphone 15 pro",
    "iphone 16",
    "iphone charger",
    "iphone case",
    "samsung s25",
    "samsung galaxy",
    "macbook air",
    "macbook pro",
    "chatgpt",
    "chatgpt login",
    "chatgpt plus",
    "chatgpt api",
    "python tutorial",
    "python projects",
    "python interview questions",
    "java tutorial",
    "java spring boot",
    "java dsa",
    "ipl score",
    "ipl schedule",
    "gta 6",
    "gta 6 trailer",
    "youtube",
    "youtube music",
    "youtube downloader",
    "github",
    "github actions",
    "github copilot",
    "leetcode",
    "docker tutorial",
    "kubernetes tutorial",
    "sql tutorial",
    "react tutorial",
    "nodejs tutorial",
    "netflix",
    "spotify",
    "whatsapp web",
    "gmail"
]

rows = []

# Popular realistic searches
for query in queries:
    rows.append({
        "query": query,
        "count": random.randint(50000, 100000)
    })

# Fill remaining rows with realistic variations
for i in range(100000 - len(rows)):
    base = random.choice(queries)

    rows.append({
        "query": f"{base} {i}",
        "count": random.randint(1, 50000)
    })

df = pd.DataFrame(rows)

df.to_csv(
    "../dataset/queries.csv",
    index=False
)

print(f"{len(df)} queries generated")