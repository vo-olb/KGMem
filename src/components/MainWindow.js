import React, { useEffect, useRef } from 'react';

function MainWindow({ messages }) {
    const bottomRef = useRef(null);

    // Scroll to the bottom whenever messages change
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="main-window">
            {messages.map((message, index) => (
                <div key={index} className={`message ${message.type}`}>
                    <span>{message.text}</span>
                </div>
            ))}
            <div ref={bottomRef}></div>
        </div>
    );
}

export default MainWindow;