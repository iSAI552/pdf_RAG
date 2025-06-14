from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


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
    images = []

    for i, page in enumerate(pages):
        image_save_path = f"/mnt/uploads/images/{id}/image_{i + 1}.jpg"
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        page.save(image_save_path, "JPEG")
        images.append(image_save_path)

        await files_collection.update_one(
            {
                "_id": ObjectId(id)
            }, {
                "$set": {
                    "status": "Successfully converted to images",
                }
            })

        images_base64 = [encode_image_to_base64(img) for img in images]
        result = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Based on the resume provide me what are the strong points and what are the weak points of the resume. "
                                "Also provide me the skills that are mentioned in the resume. "
                                "Also provide me the summary of the resume. "
                            ),
                        },
                        {
                            # flake8: noqa,this removes the large line lint error
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{images_base64[0]}",
                        }
                    ]
                }
            ]
        )
        
        response = result.output_text
        
        await files_collection.update_one(
        {
            "_id": ObjectId(id)
        }, {
            "$set": {
                "status": "Successfully processed the file",
                "result": response,
            }
        })
