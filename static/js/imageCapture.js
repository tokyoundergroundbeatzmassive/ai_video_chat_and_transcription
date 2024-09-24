export async function captureImage(streamVideo) {
    const canvas = document.createElement('canvas');
    canvas.width = streamVideo.videoWidth;
    canvas.height = streamVideo.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(streamVideo, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('file', blob, `capture_${Date.now()}.webp`);
        const response = await fetch('/save_images/', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        console.log('Image captured:', data.filename);
    }, 'image/webp');
}