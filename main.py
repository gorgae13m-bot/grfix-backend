from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
import shutil
import os
import uuid
import httpx

app = FastAPI(title="GRFix FiveM Backend API", version="1.0")

# Allow CORS so your Netlify frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ⚠️ Hna 7ott les credentials ta3 Discord Application ta3ak
DISCORD_CLIENT_ID = "1550899933693874206"
DISCORD_CLIENT_SECRET = "G17cSG5vcC87Qj08sWb3Qul3yhK0c7iI"
REDIRECT_URI = "https://grfix-backend-production.up.railway.app/auth/discord/callback"
FRONTEND_URL = "grfix-s1.netlify.app" # Rabet ta3 site ta3ek f Netlify

@app.get("/")
def read_root():
    return {"status": "GRFix Backend is Online & Ready!"}

# ==================== DISCORD OAUTH ROUTES ====================

@app.get("/auth/discord")
def auth_discord():
    discord_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={str(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope=identify"
    )
    return RedirectResponse(discord_url)

@app.get("/auth/discord/callback")
async def discord_callback(code: str):
    if not code:
        raise HTTPException(status_code=400, detail="No code provided from Discord")
    
    token_url = "https://discord.com/api/oauth2/token"
    payload = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        try:
            # Exchange code for access token
            token_res = await client.post(token_url, data=payload, headers=headers)
            if token_res.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch token from Discord")
            
            token_data = token_res.json()
            access_token = token_data.get("access_token")

            # Get user info from Discord
            user_res = await client.get(
                "https://discord.com/api/users/@me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if user_res.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch user profile from Discord")
            
            user_data = user_res.json()
            
            # Redirect back to Frontend with user data (encoded)
            import urllib.parse
            import json
            encoded_user = urllib.parse.quote(json.dumps(user_data))
            return RedirectResponse(f"{FRONTEND_URL}/?user={encoded_user}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# ==================== EXISTING API ROUTES ====================

@app.post("/api/fix-3d")
async def fix_3d_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.zip', '.yft', '.ydr', '.ytd')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload .zip or FiveM stream files.")

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    output_path = os.path.join(PROCESSED_DIR, f"fixed_{file.filename}")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        with open(input_path, "rb") as f_in:
            content = f_in.read()
        
        fixed_content = content  
        with open(output_path, "wb") as f_out:
            f_out.write(fixed_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    if os.path.exists(input_path):
        os.remove(input_path)

    return FileResponse(output_path, media_type='application/octet-stream', filename=f"fixed_{file.filename}")

@app.post("/api/decrypt")
async def decrypt_resource(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip archives are supported for decryption.")

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    output_path = os.path.join(PROCESSED_DIR, f"decrypted_{file.filename}")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        shutil.copy(input_path, output_path) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(output_path, media_type='application/zip', filename=f"decrypted_{file.filename}")