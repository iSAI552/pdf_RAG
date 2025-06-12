from fastapi import FastAPI, UploadFile, Path
# from uuid import uuid4
from .utils.file import save_to_disk
from .db.collections.files import files_collection
from .db.collections.files import FileSchema
from .queue.q import q
from .queue.workers import process_file
from bson import ObjectId


app = FastAPI()


@app.get("/")
def health():
    return {"status": "healthy"}


@app.post("/upload")
async def upload_file(file: UploadFile):
    # id = uuid4()
    # Save in MONGODB
    db_file = await files_collection.insert_one(FileSchema(
        name=file.filename,
        status="saving"
    ))

    file_path = f"/mnt/uploads/{str(db_file.inserted_id)}/{file.filename}"
    await save_to_disk(file=await file.read(), path=file_path)

    # Push to Redis queue
    q.enqueue(process_file, str(db_file.inserted_id), file_path)
    # the above returns a Job object, which is used to track pushed to queue,
    # out of queue, etc.

    await files_collection.update_one(
        {
            "_id": db_file.inserted_id
        }, {
            "$set": {
                "status": "queued",
            }
        })

    return {"file_id": str(db_file.inserted_id)}

# flake8: noqa,this removes lint errors
@app.get("/files/{id}")
async def get_file_by_id(id: str = Path(..., description="The ID of the file to retrieve")):
    db_file = await files_collection.find_one({"_id": ObjectId(id)})

    return {
        "id": str(db_file["_id"]),
        "name": db_file["name"],
        "status": db_file["status"],
        "result": db_file.get("result", None)
    }