# 08 - File Upload & Download
# Topics: UploadFile, multiple files, file validation, static files

import os
import shutil
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="File Upload & Download")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Static files serve karo
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ─── 1. Single File Upload ────────────────────────────────────────────────────
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "saved_at": file_path,
        "url": f"/static/{file.filename}",
    }


# ─── 2. Image Upload with Validation ─────────────────────────────────────────
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    # Type check
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Sirf images allowed hain. Mila: {file.content_type}",
        )

    # Size check
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File 5MB se zyada nahi honi chahiye")

    # Safe naam
    safe_name = f"{os.urandom(8).hex()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "original_name": file.filename,
        "saved_as": safe_name,
        "size_kb": round(len(contents) / 1024, 2),
        "url": f"/static/{safe_name}",
    }


# ─── 3. Multiple Files Upload ─────────────────────────────────────────────────
@app.post("/upload/multiple")
async def upload_multiple(files: List[UploadFile] = File(...)):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Ek baar mein max 10 files")

    uploaded = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded.append({"filename": file.filename, "url": f"/static/{file.filename}"})

    return {"uploaded": uploaded, "count": len(uploaded)}


# ─── 4. File + Form Data Together ────────────────────────────────────────────
@app.post("/profile/upload")
async def upload_profile(
    name: str = Form(...),
    bio: str = Form(""),
    avatar: UploadFile = File(...),
):
    if avatar.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Sirf image upload karo")

    file_path = os.path.join(UPLOAD_DIR, f"avatar_{name}_{avatar.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(avatar.file, buffer)

    return {"name": name, "bio": bio, "avatar_url": f"/static/avatar_{name}_{avatar.filename}"}


# ─── 5. File Download ─────────────────────────────────────────────────────────
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File nahi mili")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",  # Force download
    )


# ─── 6. List uploaded files ───────────────────────────────────────────────────
@app.get("/files")
def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {
        "files": [{"name": f, "url": f"/static/{f}"} for f in files],
        "count": len(files),
    }
