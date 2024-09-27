import os
from openai import OpenAI
from fastapi import HTTPException
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

async def openai_tts(image_description: str, output_dir: str):
    try:
        # 出力ファイル名を生成（タイムスタンプを使用）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"tts_output_{timestamp}.mp3"
        output_file = os.path.join(output_dir, output_filename)

        # OpenAI TTS APIを使用して音声を生成
        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",  # または "alloy", "echo", "fable", "onyx" など
            input=image_description
        )

        # 生成された音声をファイルに保存（ストリーミングを使用）
        with open(output_file, 'wb') as f:
            for chunk in response.iter_bytes():
                f.write(chunk)

        # print(f"Audio file saved to (full path): {output_file}")
        # print(f"Audio filename: {output_filename}")
        return {"audio_file": f"/tmp/{output_filename}"}

    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")