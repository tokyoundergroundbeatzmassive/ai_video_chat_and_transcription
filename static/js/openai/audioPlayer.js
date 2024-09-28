export class AudioPlayer {
    constructor(audioElement) {
        this.audioElement = audioElement;
        if (!this.audioElement) {
            console.error('Audio element is not provided');
        } else {
            console.log('Audio element found:', this.audioElement);
            // オーディオ再生終了時のイベントリスナーを追加
            this.audioElement.addEventListener('ended', this.onAudioEnded.bind(this));
            console.log('Added ended event listener');
        }
    }

    playAudio(audioUrl) {
        if (this.audioElement) {
            console.log('Playing audio:', audioUrl);
            this.audioElement.src = audioUrl;
            this.audioElement.play().catch(e => console.error('Error playing audio:', e));
        } else {
            console.error('Cannot play audio: audio element is not initialized');
        }
    }

    stopAudio() {
        if (this.audioElement) {
            console.log('Stopping audio');
            this.audioElement.pause();
            this.audioElement.currentTime = 0;
        }
    }

    onAudioEnded() {
        console.log('Audio playback ended');
        this.deleteAudioFiles();
    }

    async deleteAudioFiles() {
        try {
            const response = await fetch('/delete-audio', {
                method: 'POST',
            });
            const result = await response.json();
            console.log('Delete audio files result:', result);
        } catch (error) {
            console.error('Error deleting audio files:', error);
        }
    }
}