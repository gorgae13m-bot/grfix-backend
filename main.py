from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
import uuid

app = FastAPI(title="B7Fix FiveM Backend API", version="1.0")

# Allow CORS so your Netlify frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # F l-production, mken t-baddalha b URL ta3 site dyalk f Netlify
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "B7Fix Backend is Online & Ready!"}

@app.post("/api/fix-3d")
async def fix_3d_file(file: UploadFile = File(...)):
    """
    Endpoint خاص بإصلاح ملفات 3D (YFT / YDR) وتعديل الـ headers.
    """
    if not file.filename.endswith(('.zip', '.yft', '.ydr', '.ytd')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload .zip or FiveM stream files.")

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    output_path = os.path.join(PROCESSED_DIR, f"fixed_{file.filename}")

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # ---- HNA FIN K-T-DIR LOGIC TAJ ISLAH (Binary Processing / Parsing RSC7 headers) ----
        # Lila bghit t-qra w t-sllh l-headers ta3 YFT:
        with open(input_path, "rb") as f_in:
            content = f_in.read()
        
        # Example processing: Checking or fixing headers simulation
        # (Hna t-9dr t-zid l-code dyalk l-khass b fakk l-tashfir wla islah l-vertices)
        fixed_content = content  # Badloola b l-algorithm dyalk 
        
        with open(output_path, "wb") as f_out:
            f_out.write(fixed_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    # Clean input file
    if os.path.exists(input_path):
        os.remove(input_path)

    return FileResponse(output_path, media_type='application/octet-stream', filename=f"fixed_{file.filename}")

@app.post("/api/decrypt")
async def decrypt_resource(file: UploadFile = File(...)):
    """
    Endpoint خاص بفك تشفير سكربتات FiveM (Grants / Lura).
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip archives are supported for decryption.")

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    output_path = os.path.join(PROCESSED_DIR, f"decrypted_{file.filename}")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Logic ta3 decrypting zip contents (removing fxap/encryption wrappers)
        shutil.copy(input_path, output_path) # Simulation dyal result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(output_path, media_type='application/zip', filename=f"decrypted_{file.filename}")