from fastapi import FastAPI, UploadFile
# from uuid import uuid4
from .utils.file import save_to_disk
from .db.collections.files import files_collection
from .db.collections.files import FileSchema
from .queue.q import q
from .queue.workers import process_file


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
    q.enqueue(process_file, str(db_file.inserted_id))
    # the above returns a Job object, which is used to track pushed to queue,
    # out of queue, etc.

    await files_collection.update_one({
        "_id": db_file.inserted_id
    }, {
        "$set": {
            "status": "queued",
        }
    })

    return {"file_id": str(db_file.inserted_id)}
