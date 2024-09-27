from fastapi import APIRouter, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import glob
from src.managers.websocket_manager import manager
import os
import shutil
from src.deepgram.stream_stt import initialize_deepgram_connection, process_audio_data
from src.openai.whisper1 import transcribe_with_whisper1
from src.openai.multimodal import get_image_description
from src.openai.openai_tts import openai_tts
from src.config.config import TMP_DIR

router = APIRouter()

# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             await websocket.receive_text()
#     except:
#         manager.disconnect(websocket)

@router.get("/")
async def read_index():
    return FileResponse('static/index.html')

@router.post("/save_images/")
async def upload_file(file: UploadFile = File(...)):
    upload_dir = "tmp"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@router.websocket("/transcribe")
async def transcribe_endpoint(websocket: WebSocket):
    print("WebSocket connection opened for transcription")
    await manager.connect(websocket)

    async def send_transcript(transcript):
        await websocket.send_text(transcript)

    try:
        print("Initializing Deepgram connection")
        if not await initialize_deepgram_connection(send_transcript):
            await websocket.close()
            return

        audio_data = bytearray()
        while True:
            data = await websocket.receive_bytes()
            audio_data.extend(data)
            await process_audio_data(data)
    except Exception as e:
        print(f"WebSocket connection closed for transcription: {e}")

@router.post("/transcribe_audiofile/")
async def transcribe_audiofile_endpoint(file: UploadFile = File(...)):
    # デバッグ用ログ
    print(f"Received file: {file.filename}")

    # tmpフォルダから最新の4つのwebp画像を取得
    images = sorted(
        [f for f in os.listdir(TMP_DIR) if f.endswith(".webp")],
        key=lambda x: os.path.getmtime(os.path.join(TMP_DIR, x)),
        reverse=True
    )[:4]

    print(f"Found images: {images}")

    # 音声ファイルを転写
    transcription_result = await transcribe_with_whisper1(file, TMP_DIR)
    text = transcription_result.get("transcript", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="Transcription failed")

    # 画像のパスを生成（絶対パスを使用）
    image_paths = [os.path.join(TMP_DIR, image) for image in images]

    # 画像の説明を取得
    image_description = get_image_description(text, image_paths)

    # 音声合成のために結合された説明を使用
    tts_result = await openai_tts(image_description, TMP_DIR)

    # tmpフォルダ内のすべてのwebpファイルを削除
    webp_files = glob.glob(os.path.join(TMP_DIR, "*.webp"))
    for file in webp_files:
        try:
            os.remove(file)
            # print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

    # レスポンスを返す
    return {
        "transcript": text,
        "image_description": image_description,
        "tts_audio_file": tts_result  # この行が正しく設定されているか確認
    }

@router.post("/delete-audio")
async def delete_audio():
    try:
        # TMP_DIR内のすべてのmp3ファイルを取得
        mp3_files = glob.glob(os.path.join(TMP_DIR, "*.mp3"))
        print(f"Found mp3 files: {mp3_files}")
        
        # 各ファイルを削除
        for file in mp3_files:
            os.remove(file)
        
        return {"status": "success", "message": f"Deleted {len(mp3_files)} mp3 file(s)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting mp3 files: {str(e)}")