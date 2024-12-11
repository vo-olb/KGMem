import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

function MainWindow({ messages }) {
    const bottomRef = useRef(null);

    // Scroll to the bottom whenever messages change
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="main-window">
            {messages.map((message, index) => (
                <div key={index} className={`message ${message.type} markdown-content`}>
                    <ReactMarkdown>
                        {message.text}
                    </ReactMarkdown>
                </div>
            ))}
            <div ref={bottomRef}></div>
        </div>
    );
}

export default MainWindow;