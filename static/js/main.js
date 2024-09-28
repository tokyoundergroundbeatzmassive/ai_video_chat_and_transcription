import { startAudioCapture } from './deepgram/audioCapture.js';
import { startWebSocket, stopWebSocket } from './managers/websocket.js';
import { AudioRecorder } from './openai/audioRecorder.js';

const startCameraBtn = document.getElementById('startCameraBtn');
const startWindowBtn = document.getElementById('startWindowBtn');
const stopBtn = document.getElementById('stopBtn');
const statusElement = document.getElementById('status');
const streamVideo = document.getElementById('streamVideo');
const transcribeBtn = document.getElementById('transcribeBtn');
const recordBtn = document.getElementById('recordBtn');
const audioRecorder = new AudioRecorder(streamVideo, statusElement);

let stream;
let isCameraActive = false;

recordBtn.addEventListener('mousedown', () => audioRecorder.startRecording(isCameraActive));
recordBtn.addEventListener('mouseup', () => audioRecorder.stopRecording());
recordBtn.addEventListener('mouseleave', () => audioRecorder.stopRecording());

transcribeBtn.addEventListener('click', async () => {
    // WebSocket接続を開始
    const socket = startWebSocket(`ws://${window.location.host}/transcribe`, async (event) => {
        if (typeof event.data === 'string') {
            // 文字列データ（おそらく転写結果）を受信した場合
            console.log('Received transcription:', event.data);
            // ここで受信したテキストを適切に表示する処理を追加
            // 例: statusElement.textContent = `Transcription: ${event.data}`;
        } else if (event.data instanceof Blob) {
            // Blobデータ（おそらくビデオデータ）を受信した場合
            const videoUrl = URL.createObjectURL(event.data);
            streamVideo.src = videoUrl;
        } else {
            console.warn('Received unknown data type:', typeof event.data);
        }
    }, async () => {
        // オーディオキャプチャを開始
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            startAudioCapture(socket, stream);
        } catch (err) {
            console.error('オーディオのアクセスに失敗しました:', err);
        }
    });
});

startCameraBtn.addEventListener('click', async () => {
    // カメラの映像を取得して表示
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        streamVideo.srcObject = stream;
        statusElement.textContent = "Camera stream started";
        isCameraActive = true;
    } catch (err) {
        console.error('カメラのアクセスに失敗しました:', err);
        statusElement.textContent = "Failed to start camera stream";
        isCameraActive = false;
    }
});

startWindowBtn.addEventListener('click', async () => {
    // ウィンドウの映像を取得して表示
    try {
        stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
        streamVideo.srcObject = stream;
        statusElement.textContent = "Window stream started";

        // Stream Audioをミュート
        streamVideo.muted = true;

        // オーディオキャプチャを開始
        const socket = startWebSocket(`ws://${window.location.host}/transcribe`, async (event) => {
            if (typeof event.data === 'string') {
                // 文字列データ（おそらく転写結果）を受信した場合
                console.log('Received transcription:', event.data);
                // ここで受信したテキストを適切に表示する処理を追加
                // 例: statusElement.textContent = `Transcription: ${event.data}`;
            } else if (event.data instanceof Blob) {
                // Blobデータ（おそらくビデオデータ）を受信した場合
                const videoUrl = URL.createObjectURL(event.data);
                streamVideo.src = videoUrl;
            } else {
                console.warn('Received unknown data type:', typeof event.data);
            }
        }, async () => {
            startAudioCapture(socket, stream);
        });
    } catch (err) {
        console.error('ウィンドウのアクセスに失敗しました:', err);
        statusElement.textContent = "Failed to start window stream";
    }
});

stopBtn.addEventListener('click', () => {
    stopWebSocket();
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
    }
    streamVideo.srcObject = null;
    statusElement.textContent = "Stream stopped";
});