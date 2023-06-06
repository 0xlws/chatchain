from discord_bot.utils.setup_handler import SetupHandler
from plugins.vector_store.chroma_manager import ChromaManager

chroma_manager = ChromaManager()

db = ChromaManager("discord")
collection = db.collection


class VectorDBPlugin(SetupHandler):
    def setup(self):
        """"""
