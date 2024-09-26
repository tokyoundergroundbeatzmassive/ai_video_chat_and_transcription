from fastapi import APIRouter, WebSocket, UploadFile, File
from fastapi.responses import FileResponse
from src.managers.websocket_manager import manager
import os
import shutil
from src.deepgram.stt import initialize_deepgram_connection, process_audio_data, close_deepgram_connection
from pydub import AudioSegment
import requests
import dotenv
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

dotenv.load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

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
    upload_dir = "temp"
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
        # print(f"Sending transcript to client: {transcript}")  # デバッグメッセージ
        await websocket.send_text(transcript)

    try:
        print("Initializing Deepgram connection")  # デバッグメッセージ
        if not await initialize_deepgram_connection(send_transcript):
            await websocket.close()
            return

        audio_data = bytearray()
        while True:
            data = await websocket.receive_bytes()
            # print("Received audio data:", data[:10])
            audio_data.extend(data)
            await process_audio_data(data)
    except Exception as e:
        print(f"WebSocket connection closed for transcription: {e}")
    # finally:
    #     # Save the received audio data to an MP3 file for debugging
    #     sample_rate = 44100  # JavaScript側で取得したサンプリングレートに合わせる
    #     audio_segment = AudioSegment(
    #         data=bytes(audio_data),
    #         sample_width=2,  # Assuming 16-bit audio
    #         frame_rate=sample_rate,  # JavaScript側で取得したサンプリングレート
    #         channels=1  # Assuming mono audio
    #     )
    #     output_path = os.path.join(os.getcwd(), "received_audio.mp3")
    #     audio_segment.export(output_path, format="mp3")
    #     print(f"Saved received audio to {output_path}")

    #     manager.disconnect(websocket)
    #     await close_deepgram_connection()

@router.post("/transcribe_audiofile/")
async def transcribe_audiofile(file: UploadFile = File(...)):
    try:
        # ファイルの詳細情報をログに出力
        print(f"Received file: {file.filename}")
        print(f"Content type: {file.content_type}")

        # ファイルを一時的に保存
        temp_file_path = "/tmp/temp_audio_file.webm"
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        print(f"Saved temporary file to: {temp_file_path}")

        # OpenAIのWhisper APIを使用して転写
        with open(temp_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ja"
            )
        
        transcript = transcription.text
        print(f"Transcription result: {transcript}")
        return {"transcript": transcript}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}