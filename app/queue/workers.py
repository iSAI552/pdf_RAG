from ..db.collections.files import files_collection
from bson import ObjectId


async def process_file(id: str):
    print(f"Processing file with ID: {id}")
  
    await files_collection.update_one({
        "_id": ObjectId(id)
    }, {
        "$set": {
            "status": "processing",
        }
    })
    