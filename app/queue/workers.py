from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
import os


async def process_file(id: str, file_path: str):
    print(f"Processing file with ID: {id}")

    await files_collection.update_one(
        {
            "_id": ObjectId(id)
        }, {
            "$set": {
                "status": "processing",
            }
        })

    # Step 1: Convert the pdf to image as resume can be in various formats,
    # non ATS friendly also

    await files_collection.update_one(
        {
            "_id": ObjectId(id)
        }, {
            "$set": {
                "status": "converting to images",
            }
        })

    pages = convert_from_path(file_path)

    for i, page in enumerate(pages):
        image_save_path = f"/mnt/uploads/images/{id}/image_{i + 1}.jpg"
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        page.save(image_save_path, "JPEG")

        await files_collection.update_one(
            {
                "_id": ObjectId(id)
            }, {
                "$set": {
                    "status": "Successfully converted to images",
                }
            })
