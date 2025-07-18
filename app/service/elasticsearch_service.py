from elasticsearch import AsyncElasticsearch
import os


es_url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es = AsyncElasticsearch(hosts=[es_url])


async def index_user(user):
    doc = {
        "name": user.name,
        "email": user.email,
    }
    await es.index(index="users", id=user.id, document=doc)
    await es.indices.refresh(index="users")

async def search_users(query: str):
    response = await es.search(index="users", query={
        "multi_match": {
            "query": query,
            "fields": ["name", "email"],
            "fuzziness": "AUTO"

        }
    })
    print("ES response:", response) 
    return response["hits"]["hits"]
