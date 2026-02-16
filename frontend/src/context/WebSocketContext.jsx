import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const [socket, setSocket] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);
    const reconnectTimeoutRef = useRef(null);

    const connect = useCallback(() => {
        // In a real app, user_id would come from auth context
        const userId = "user-" + Math.floor(Math.random() * 10000);
        // Use relative path for WebSocket (proxied by Vite)
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${userId}`;

        console.log("Connecting to WebSocket:", wsUrl);
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("WebSocket Connected");
            setIsConnected(true);
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
                reconnectTimeoutRef.current = null;
            }
        };

        ws.onclose = () => {
            console.log("WebSocket Disconnected");
            setIsConnected(false);

            // Attempt reconnect after 3 seconds
            reconnectTimeoutRef.current = setTimeout(() => {
                console.log("Attempting reconnect...");
                connect();
            }, 3000);
        };

        ws.onerror = (error) => {
            console.error("WebSocket Error:", error);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("WebSocket Message:", data);
                setLastMessage(data);
            } catch (e) {
                console.error("Failed to parse WebSocket message:", e);
            }
        };

        setSocket(ws);

        return () => {
            ws.close();
        };
    }, []);

    useEffect(() => {
        const cleanup = connect();
        return () => {
            if (cleanup) cleanup();
            if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        };
    }, [connect]);

    const sendMessage = useCallback((message) => {
        if (socket && isConnected) {
            socket.send(JSON.stringify(message));
        } else {
            console.warn("WebSocket is not connected. Cannot send message.");
        }
    }, [socket, isConnected]);

    return (
        <WebSocketContext.Provider value={{ socket, isConnected, lastMessage, sendMessage }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => {
    const context = useContext(WebSocketContext);
    if (!context) {
        throw new Error('useWebSocket must be used within a WebSocketProvider');
    }
    return context;
};
