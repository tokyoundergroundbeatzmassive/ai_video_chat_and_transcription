export async function startAudioCapture(socket, stream) {
    try {
        console.log('Starting audio capture...');
        const audioContext = new AudioContext();

        // AudioWorkletを追加
        await audioContext.audioWorklet.addModule('static/js/audioProcessor.js');
        const audioProcessor = new AudioWorkletNode(audioContext, 'audio-processor');

        let packetCount = 0;
        audioProcessor.port.onmessage = (event) => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                const audioData = event.data;
                // Float32ArrayをInt16Arrayに変換
                const int16Data = new Int16Array(audioData.length);
                for (let i = 0; i < audioData.length; i++) {
                    int16Data[i] = Math.max(-1, Math.min(1, audioData[i])) * 0x7FFF;
                }
                socket.send(int16Data.buffer);
                packetCount++;
                if (packetCount % 100 === 0) {  // 100パケットごとにログを出力
                    // console.log(`Sent ${packetCount} audio packets`);
                }
            }
        };

        // ウィンドウの音声トラックを取得
        const windowAudioTracks = stream.getAudioTracks();
        if (windowAudioTracks.length > 0) {
            const windowAudioTrack = windowAudioTracks[0];
            const windowSource = audioContext.createMediaStreamSource(new MediaStream([windowAudioTrack]));
            windowSource.connect(audioProcessor);
        } else {
            console.warn('No window audio tracks found');
        }

        // マイクの音声トラックを取得
        const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const micAudioTracks = micStream.getAudioTracks();
        if (micAudioTracks.length > 0) {
            const micAudioTrack = micAudioTracks[0];
            const micSource = audioContext.createMediaStreamSource(new MediaStream([micAudioTrack]));
            micSource.connect(audioProcessor);
        } else {
            console.warn('No microphone audio tracks found');
        }

        // audioProcessor.connect(audioContext.destination);
        console.log('Audio capture and processing setup complete');
    } catch (err) {
        console.error('オーディオのアクセスに失敗しました:', err);
    }
}