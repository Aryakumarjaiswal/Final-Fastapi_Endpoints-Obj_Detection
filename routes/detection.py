from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
import os
import time
from app.database import get_db
from app.models.models import Inventory
from app.services.analysis_services import process_image, process_image_data_add, process_video, process_maintenance_check
# from app.services.database import rollback_transaction, commit_transaction
import uuid
from sqlalchemy.orm import Session

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os
import time
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.database import get_db
from app.services.analysis_services import process_image
router = APIRouter()

UPLOAD_DIR_IMG = "static/uploads/images"
UPLOAD_DIR_VID = "static/uploads/videos"
os.makedirs(UPLOAD_DIR_IMG, exist_ok=True)
os.makedirs(UPLOAD_DIR_VID, exist_ok=True)


# @router.post("/images")
# async def analyze_images(
#     task_id: int, 
#     media_files: List[UploadFile] = File(...), 
#     db: Session = Depends(get_db)
# ):
#     try:
#         start_time=time.time()
#         results = []
#         for media_file in media_files:
#             unique_filename = f"detection_image_{uuid.uuid4()}_{media_file.filename}"
#             file_path = os.path.join(UPLOAD_DIR_IMG, unique_filename)

#             # Save uploaded file to disk
#             with open(file_path, "wb") as f:
#                 f.write(await media_file.read())

        
#             # Process image and store results
#             result = await process_image(file_path=file_path, media_type="image", task_id=task_id, db=db)
#             results.append(result)
            

#         return {"results": results}

#     except Exception as e:
#         db.rollback()
#         return {"error occured": str(e)}, 500









router = APIRouter()

UPLOAD_DIR_IMG = "static/uploads/images"



@router.post("/images")
async def analyze_images(
    task_id: int, 
    media_files: List[UploadFile] = File(...), 
    db: Session = Depends(get_db)  # Ensure db is passed
):
    try:
        start_time = time.time()
        file_paths = []

        # Save uploaded files
        for media_file in media_files:
            unique_filename = f"detection_image_{uuid.uuid4()}_{media_file.filename}"
            file_path = os.path.join(UPLOAD_DIR_IMG, unique_filename)

            with open(file_path, "wb") as f:
                f.write(await media_file.read())

            file_paths.append(file_path)

        if not file_paths:
            raise HTTPException(status_code=400, detail="No files were uploaded")

        # Parallel processing using ThreadPoolExecutor
        loop = asyncio.get_running_loop()
        results = []

        with ThreadPoolExecutor(max_workers=min(4, os.cpu_count())) as executor:
            inference_tasks = [
                loop.run_in_executor(
                    executor,
                    process_image,  # No need for `asyncio.run`
                    file_path,
                    "image",
                    task_id
                     # Pass DB session
                )
                for file_path in file_paths
            ]
            inference_results = await asyncio.gather(*inference_tasks)

        results.extend(inference_results)  # Store results

        end_time = time.time()
        print("Execution time:", end_time - start_time)

        return {"results": results}

    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})
@router.post("/video")
async def analyze_video(task_id: int, media_file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        unique_filename = f"detection_video_{media_file.filename}_{uuid.uuid4()}.mp4"
        file_path = os.path.join(UPLOAD_DIR_VID, unique_filename)
        with open(file_path, "wb") as f:
            f.write(await media_file.read())

        result = process_video(file_path=file_path, media_type="video", task_id=task_id, db=db)

        return JSONResponse(content={"result": result})
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)
