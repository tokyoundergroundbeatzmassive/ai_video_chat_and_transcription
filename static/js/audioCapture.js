export async function startAudioCapture(socket) {
    try {
        console.log('Starting audio capture...');
        const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log('Audio stream obtained');
        const audioTracks = audioStream.getAudioTracks();
        if (audioTracks.length > 0) {
            const audioTrack = audioTracks[0];
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

            const source = audioContext.createMediaStreamSource(new MediaStream([audioTrack]));
            source.connect(audioProcessor);
            audioProcessor.connect(audioContext.destination);

            console.log('Audio capture and processing setup complete');
        } else {
            console.warn('No audio tracks found');
        }
    } catch (err) {
        console.error('オーディオのアクセスに失敗しました:', err);
    }
}