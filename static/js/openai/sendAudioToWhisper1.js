import { AudioPlayer } from './audioPlayer.js';

let audioPlayer;

export function initAudioPlayer(audioElement) {
    audioPlayer = new AudioPlayer(audioElement);
}

export async function sendAudioToWhisper1(audioBlob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.webm');
    try {
        const response = await fetch('/transcribe_audiofile/', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        console.log('Response data:', data);

        if (data.transcript && data.image_description && data.tts_audio_file) {
            console.log('Transcript:', data.transcript);
            console.log('Image Description:', data.image_description);
            console.log('TTS Audio File:', data.tts_audio_file);

            // 音声を再生（audioPlayerが初期化されているか確認）
            if (audioPlayer) {
                audioPlayer.playAudio(data.tts_audio_file.audio_file);
            } else {
                console.error('AudioPlayer is not initialized');
            }

            return {
                transcript: data.transcript,
                imageDescription: data.image_description,
                audioUrl: data.tts_audio_file.audio_file
            };
        } else {
            console.warn('転写結果、画像の説明、または音声ファイルが見つかりませんでした。');
            console.warn('Missing data:', {
                transcript: !!data.transcript,
                image_description: !!data.image_description,
                tts_audio_file: !!data.tts_audio_file
            });
            return null;
        }
    } catch (err) {
        console.error('Transcription APIへの送信に失敗しました:', err);
        return null;
    }
}

// DOMContentLoadedイベントで初期化
document.addEventListener('DOMContentLoaded', () => {
    const audioElement = document.getElementById('audioPlayer');
    if (audioElement) {
        initAudioPlayer(audioElement);
    } else {
        console.error('Audio element not found');
    }
});