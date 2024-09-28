let socket;

export function startWebSocket(url, onMessage, onOpen, onClose, onError) {
    socket = new WebSocket(url);
    socket.binaryType = 'arraybuffer';

    socket.onopen = () => {
        console.log('WebSocket接続が開かれました');
        if (onOpen) onOpen();
    };

    socket.onmessage = (event) => {
        console.log('メッセージを受信しました。データタイプ:', typeof event.data);
        if (typeof event.data === 'string') {
            console.log('受信したテキストデータ:', event.data);
        } else if (event.data instanceof ArrayBuffer) {
            console.log('バイナリデータを受信しました。サイズ:', event.data.byteLength, 'バイト');
        } else if (event.data instanceof Blob) {
            console.log('Blobデータを受信しました。サイズ:', event.data.size, 'バイト');
        } else {
            console.log('不明なデータ型');
        }
        if (onMessage) onMessage(event);
    };

    socket.onerror = (error) => {
        console.error('WebSocketエラー:', error);
        if (onError) onError(error);
    };

    socket.onclose = () => {
        console.log('WebSocket接続が閉じられました');
        if (onClose) onClose();
    };

    return socket;
}

export function stopWebSocket() {
    if (socket) {
        socket.close();
    }
}