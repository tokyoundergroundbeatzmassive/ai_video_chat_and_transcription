import { captureImage } from './imageCapture.js';
import { sendAudioToWhisper1 } from './sendAudioToWhisper1.js';

export class AudioRecorder {
    constructor(streamVideo, statusElement) {
        this.streamVideo = streamVideo;
        this.statusElement = statusElement;
        this.isRecording = false;
        this.captureInterval = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
    }

    async startRecording(isCameraActive) {
        if (isCameraActive) {
            this.isRecording = true;
            this.captureInterval = setInterval(() => {
                if (this.isRecording) {
                    captureImage(this.streamVideo);
                }
            }, 1000);
        }
        try {
            const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.audioChunks = [];
                await sendAudioToWhisper1(audioBlob);
            };
            this.mediaRecorder.start();
            this.statusElement.textContent = "Recording...";
        } catch (err) {
            console.error('オーディオのアクセスに失敗しました:', err);
            this.statusElement.textContent = "Failed to access audio";
        }
    }

    stopRecording() {
        if (this.isRecording) {
            clearInterval(this.captureInterval);
            this.isRecording = false;
        }
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
            this.statusElement.textContent = "Recording stopped";
        }
    }
}