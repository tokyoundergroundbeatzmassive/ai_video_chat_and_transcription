export async function sendAudioToWhisper1(audioBlob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.mpeg');
    try {
        const response = await fetch('/transcribe_audiofile/', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        // console.log('Transcription:', data);

        // 転写結果を抽出して表示
        if (data.transcript) {
            const transcript = data.transcript;
            console.log('Transcript:', transcript);
            // ここで転写結果を表示する処理を追加
            const statusElement = document.getElementById('status');
            statusElement.textContent = `Transcription: ${transcript}`;
        } else {
            console.warn('転写結果が見つかりませんでした。');
        }
    } catch (err) {
        console.error('Transcription APIへの送信に失敗しました:', err);
    }
}