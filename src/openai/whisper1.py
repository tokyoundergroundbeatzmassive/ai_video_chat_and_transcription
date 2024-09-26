from fastapi import UploadFile, File
import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

async def transcribe_with_whisper1(file: UploadFile = File(...)):
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