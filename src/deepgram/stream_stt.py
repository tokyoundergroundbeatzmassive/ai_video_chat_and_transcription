import logging
import os
import asyncio
from datetime import datetime
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    DeepgramClientOptions
)

# ログファイルのパスを設定する関数
def get_log_file_path():
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"transcription_log_{current_time}.txt"
    return os.path.join(os.getcwd(), file_name)

# グローバル変数としてログファイルのパスを保持
log_file_path = None

API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Set up client configuration
config = DeepgramClientOptions(
    verbose=logging.WARN,  # Change to logging.INFO or logging.DEBUG for more verbose output
    options={"keepalive": "true"}
)

deepgram = DeepgramClient(API_KEY, config)

dg_connection = None

main_loop = asyncio.get_event_loop()

async def initialize_deepgram_connection(callback):
    global dg_connection
    global log_file_path
    
    # 新しいログファイルパスを生成
    log_file_path = get_log_file_path()
    print(f"New transcription session started. Log file: {log_file_path}")
    
    dg_connection = deepgram.listen.live.v("1")

    def on_open(self, open, **kwargs):
        print("on_open")  # デバッグメッセージ

    def on_close(self, close, **kwargs):
        print("on_close")  # デバッグメッセージ
        # WebSocket接続が閉じられたときに新しいログファイルを準備
        global log_file_path
        log_file_path = get_log_file_path()
        print(f"WebSocket closed. New log file prepared: {log_file_path}")

    def on_error(self, error, **kwargs):
        print(f"on_error: {error}")  # デバッグメッセージ

    def on_message(self, result, **kwargs):
        global log_file_path  # グローバル変数を使用
        print("Full response:")
        print(result)
        try:
            alternatives = result.channel.alternatives
            for alternative in alternatives:
                if hasattr(alternative, 'words') and alternative.words:
                    # 話者ごとのトランスクリプトを格納する辞書
                    speaker_transcripts = {}
                    current_speaker = None
                    current_transcript = []

                    for word in alternative.words:
                        if word.speaker != current_speaker:
                            if current_speaker is not None:
                                speaker_transcripts[current_speaker] = " ".join(current_transcript)
                            current_speaker = word.speaker
                            current_transcript = []
                        current_transcript.append(word.word)

                    # 最後の話者のトランスクリプトを追加
                    if current_speaker is not None:
                        speaker_transcripts[current_speaker] = " ".join(current_transcript)

                    for speaker, transcript in speaker_transcripts.items():
                        print(f"Speaker {speaker}: {transcript}")
                        # ファイルに書き込む
                        with open(log_file_path, "a", encoding="utf-8") as log_file:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_file.write(f"[{timestamp}] Speaker {speaker}: {transcript}\n")
                        asyncio.run_coroutine_threadsafe(callback(f"Speaker {speaker}: {transcript}"), main_loop)
                else:
                    transcript = alternative.transcript
                    if len(transcript) > 0:
                        print(f"Unknown Speaker: {transcript}")
                        # ファイルに書き込む
                        with open(log_file_path, "a", encoding="utf-8") as log_file:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_file.write(f"[{timestamp}] Unknown Speaker: {transcript}\n")
                        asyncio.run_coroutine_threadsafe(callback(f"Unknown Speaker: {transcript}"), main_loop)
        except Exception as e:
            print(f"Error processing result: {e}")
            print(f"Result: {result}")

    print("Setting up event handlers")  # デバッグメッセージ
    dg_connection.on(LiveTranscriptionEvents.Open, on_open)
    # print("Event handler for Open set")  # デバッグメッセージ
    dg_connection.on(LiveTranscriptionEvents.Close, on_close)
    # print("Event handler for Close set")  # デバッグメッセージ
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)
    # print("Event handler for Error set")  # デバッグメッセージ
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    print("Event handler for Transcript set") 

    options = LiveOptions(
        model="nova-2",
        language="ja-JP",
        encoding="linear16",
        sample_rate=44100,
        diarize=True,
        multichannel=True)
    
    print("Starting Deepgram connection")  # デバッグメッセージ
    if not dg_connection.start(options):
        print("Failed to start Deepgram connection")
        return False
    print("Deepgram connection started successfully")  # デバッグメッセージ
    return True

async def process_audio_data(data):
    if dg_connection:
        # print("Sending audio data to Deepgram")  # デバッグメッセージ
        dg_connection.send(data)

async def close_deepgram_connection():
    if dg_connection:
        print("Closing Deepgram connection")  # デバッグメッセージ
        dg_connection.send({"type": "Finalize"})
        dg_connection.finish()
