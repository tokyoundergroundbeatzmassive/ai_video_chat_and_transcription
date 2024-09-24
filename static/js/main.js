import { startAudioCapture } from './audioCapture.js';
import { captureImage } from './imageCapture.js';
import { startWebSocket, stopWebSocket } from './websocket.js';

const startCameraBtn = document.getElementById('startCameraBtn');
const startWindowBtn = document.getElementById('startWindowBtn');
const stopBtn = document.getElementById('stopBtn');
const captureBtn = document.getElementById('captureBtn');
const statusElement = document.getElementById('status');
const streamVideo = document.getElementById('streamVideo');
const transcribeBtn = document.getElementById('transcribeBtn');

let stream;
let captureInterval;

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
        startAudioCapture(socket);
    });
});

startCameraBtn.addEventListener('click', async () => {
    // カメラの映像を取得して表示
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        streamVideo.srcObject = stream;
        statusElement.textContent = "Camera stream started";
    } catch (err) {
        console.error('カメラのアクセスに失敗しました:', err);
        statusElement.textContent = "Failed to start camera stream";
    }
});

startWindowBtn.addEventListener('click', async () => {
    // ウィンドウの映像を取得して表示
    try {
        stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        streamVideo.srcObject = stream;
        statusElement.textContent = "Window stream started";
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

// image captureの機能
captureBtn.addEventListener('mousedown', () => {
    captureInterval = setInterval(() => captureImage(streamVideo), 1000);
});

captureBtn.addEventListener('mouseup', () => {
    clearInterval(captureInterval);
});

captureBtn.addEventListener('mouseleave', () => {
    clearInterval(captureInterval);
});