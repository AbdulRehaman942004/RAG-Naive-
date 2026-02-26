import chromadb
from extraction import text_list

# Create a persistent client (so you can access the collection later)
client = chromadb.PersistentClient(path="chromadb_data")

collection = client.create_collection(name="Oxford-Guide-2022")

chunks = text_list
chunks_ids = [f"chunk_{i}" for i in range(len(chunks))]

collection.add(
    ids=chunks_ids,
    documents=chunks
)

for i in range(100, 150):
    print(f"{chunks_ids[i]} : {chunks[i]} \n")