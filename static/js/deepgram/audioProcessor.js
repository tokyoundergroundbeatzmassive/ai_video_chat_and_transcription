class AudioProcessor extends AudioWorkletProcessor {
    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input.length > 0) {
            const channelData = input[0];
            // デバッグ用にデータの一部をコンソールに出力
            // console.log('Captured audio data:', channelData.slice(0, 10));
            this.port.postMessage(channelData);
        }
        return true;
    }
}

registerProcessor('audio-processor', AudioProcessor);