from typing import List, Tuple

import chromadb

from extraction import text_list


client = chromadb.PersistentClient(path="chromadb_data")


def ingest_chunks_into_chromadb(
    chunks: List[str],
    collection_name: str = "Oxford-Guide-2022",
) -> Tuple[chromadb.Collection, List[str]]:
    """Ingest a list of chunks into a persistent ChromaDB collection."""
    collection = client.get_or_create_collection(name=collection_name)
    chunks_ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(ids=chunks_ids, documents=chunks)
    return collection, chunks_ids


if __name__ == "__main__":
    # Preserve original behaviour when run as a script
    collection, chunks_ids = ingest_chunks_into_chromadb(text_list)
    for i in range(100, 150):
        print(f"{chunks_ids[i]} : {text_list[i]} \n")