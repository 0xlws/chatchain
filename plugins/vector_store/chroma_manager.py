from typing import List
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import json
import re
import hashlib
import os
from plugins.config.config_env import OPENAI_API_KEY


script_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(script_dir, "db")

if not os.path.exists(db_dir):
    os.makedirs(db_dir)
    print(f"Directory '{db_dir}' created.")


chroma_persist_directory = db_dir
host = "local"
notebook = False

chroma_persist_directory = chroma_persist_directory
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY, model_name="text-embedding-ada-002"
)

if notebook:
    chroma_persist_directory = "/content/drive/MyDrive/db"

if host == "local":
    chroma_settings = Settings(
        chroma_db_impl="duckdb+parquet", persist_directory=chroma_persist_directory
    )
else:
    chroma_settings = Settings(
        chroma_api_impl="rest",
        chroma_server_host="localhost",
        chroma_server_http_port="8000",
    )

client = chromadb.Client(chroma_settings)


class ChromaManager:
    def __init__(self, collection_name=""):
        if collection_name:
            self.collection_name = collection_name
            self.collection = self.get_or_create_collection(self.collection_name)

    @staticmethod
    def find_boundary_position(text, max_words):
        boundary_pos = max_words
        match = re.search(r"\b", text[boundary_pos:])
        if match:
            boundary_pos += match.start()
        return boundary_pos

    @staticmethod
    def separate_sentences(text):
        return text.replace(". ", ".\n")

    @staticmethod
    def chunk_text(text, max_words=128, overlap_percent=10, min_remainder_words=25):
        # text = ' '.join(text)

        words = text.split()
        if len(words) <= max_words:
            return [text]

        overlap_words = int(max_words * overlap_percent / 100)
        chunks = []
        start = 0
        end = max_words

        while end < len(words):
            if end < len(words) - min_remainder_words:
                boundary_pos = ChromaManager.find_boundary_position(text, end)
                end = boundary_pos

                chunk = " ".join(words[start:end])
                chunks.append(chunk)

                start = end - overlap_words
                end = start + max_words
            else:
                chunk = " ".join(words[start:])
                chunks.append(chunk)
                break

        return chunks

    def list_collections(self):
        collection_names = [collection.name for collection in client.list_collections()]
        return collection_names

    def get_or_create_collection(self, collection_name="", embedding_function=None):
        # if embedding_function is None:
        #     embedding_function = openai_ef
        return client.get_or_create_collection(
            collection_name if collection_name else self.collection_name
        )

    def delete_collection(self):
        return client.delete_collection(self.collection_name)

    def upload_vectors_to_chroma(self, vector, document, metadata={}):
        collection = self.get_or_create_collection(self.collection_name)

        upsert_response = collection.add(
            ids=[str(collection.count())],
            documents=[document],
            embeddings=[vector],
            metadatas=metadata,
        )
        self.persist()
        return upsert_response

    def upload_documents_to_chroma(
        self, collection, documents, sha256_hash="", metadatas=None, ids=None
    ):
        print(len(documents))
        if isinstance(metadatas, dict):
            metadatas = [metadatas]
        if isinstance(documents, str):
            documents = [documents]
        if metadatas is None:
            metadatas = [{"sha256_hash": sha256_hash}] * len(documents)
        if ids is None:
            ids = [
                str(i)
                for i in range(collection.count(), collection.count() + len(documents))
            ]

        if not len(metadatas) == len(ids):
            metadatas = metadatas * len(ids)

        upsert_response = collection.add(
            ids=ids, documents=documents, metadatas=metadatas
        )
        self.persist()
        return upsert_response

    def upload_chat_vectors_to_chroma(self, vector, message="chat_test"):
        collection = self.get_or_create_collection(self.collection_name)
        metadata = {
            "channel_name": message.channel.name,
            "author": message.author.name,
            "timestamp": str(message.created_at),
            "jump_url": str(message.jump_url),
            "message_length": len(message.content),
        }

        upsert_response = collection.add(
            ids=[str(collection.count())],
            documents=[message.content],
            embeddings=[vector],
            metadatas=metadata,
        )
        self.persist()
        return upsert_response

    @staticmethod
    def generate_file_hash(file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as file:
            for byte_block in iter(lambda: file.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def chunk_upload(self, collection, text: list):
        chunked_text = self.chunk_text(text)
        # for chunk in chunked_text:
        # vector = self.generate_text_embedding(chunk)
        self.upload_documents_to_chroma(collection, chunked_text)

    def count(self, collection_name):
        collection = self.get_or_create_collection(collection_name=collection_name)
        return collection.count()

    def query_collection(
        self,
        query_vector,
        n_results=1,
        include=["embeddings", "metadatas", "distances"],
    ):
        collection = self.get_or_create_collection(self.collection_name)
        try:
            search_response = collection.query(
                query_embeddings=[query_vector]
                if not isinstance(query_vector, List)
                else query_vector,
                include=include,
                n_results=n_results,
            )
        except Exception as e:
            print(e)

        return search_response

    async def find_similar_matches(
        self,
        query,
        top_results=5,
        embeddings=None,
        filters={},
        include=["distances", "metadatas", "documents"],
    ):
        collection = self.get_or_create_collection(self.collection_name)
        print("collection", collection)
        max_results = collection.count()

        print("max_results")
        print(max_results)

        search_results = collection.query(
            # query_embeddings=[query_vector],
            query_texts=[query],
            n_results=top_results if top_results <= max_results else max_results,
            include=include,
            where=filters,
        )

        if len(search_results) == 0:
            return None
        print(search_results)

        return search_results

    def build_metadata(self, message):
        return {
            "channel_name": message.channel.name,
            "author": message.author.name,
            "timestamp": str(message.created_at),
            "jump_url": str(message.jump_url),
            "message_length": len(message.content),
        }

    def format_text_documents(self, json_content):
        data = json.loads(json_content)
        formatted_text = ""

        for i, document in enumerate(data["documents"][0]):
            id_number = data["ids"][0][i]
            distance = data["distances"][0][i]
            url = data["metadatas"][0][i]["url"]

            formatted_text += (
                f"> {document}\nID: {id_number}\nDistance: {distance}\n[{i}]({url})\n\n"
            )

        return formatted_text

    def format_text_documents_list(self, json_content):
        data = json.loads(json_content)
        formatted_list = []

        for i, document in enumerate(data["documents"][0]):
            id_number = data["ids"][0][i]
            distance = data["distances"][0][i]
            url = data["metadatas"][0][i]["url"]

            formatted_document = f"> {document}\n"
            formatted_info = f"ID: {id_number}\nDistance: {distance}\n"
            formatted_url = f"Source: ___{url}___\n\n"
            formatted_list.append([formatted_document, formatted_info, formatted_url])

        return formatted_list
