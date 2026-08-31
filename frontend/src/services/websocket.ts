type MessageHandler = (data: any) => void;

class WebSocketClient {
  private socket: WebSocket | null = null;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectInterval: number = 3000;
  private isConnecting: boolean = false;

  public connect(channel: string = 'all') {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return;
    }
    if (this.isConnecting) return;

    this.isConnecting = true;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/telemetry?channel=${channel}`;

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        this.isConnecting = false;
        console.log('🔗 WebSocket connected to NetOps Telemetry Gateway');
      };

      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const type = message.type || 'telemetry';
          const typeHandlers = this.handlers.get(type);
          if (typeHandlers) {
            typeHandlers.forEach((h) => h(message));
          }
          const allHandlers = this.handlers.get('*');
          if (allHandlers) {
            allHandlers.forEach((h) => h(message));
          }
        } catch (e) {
          // ignore non-json messages
        }
      };

      this.socket.onclose = () => {
        this.isConnecting = false;
        this.socket = null;
        setTimeout(() => this.connect(channel), this.reconnectInterval);
      };

      this.socket.onerror = () => {
        this.isConnecting = false;
        if (this.socket) {
          this.socket.close();
        }
      };
    } catch (e) {
      this.isConnecting = false;
    }
  }

  public subscribe(eventType: string, handler: MessageHandler) {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler);

    return () => {
      this.handlers.get(eventType)?.delete(handler);
    };
  }
}

export const wsClient = new WebSocketClient();
