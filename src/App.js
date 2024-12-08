import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MainWindow from './components/MainWindow';
import InputArea from './components/InputArea';
import MemoryManager from './components/MemoryManager';
import MemoryManagementWindow from './components/MemoryManagementWindow';
import Sidebar from './components/Sidebar';

function App() {
    const test_msgs = [
        { type: 'bot', text: 'Welcome to the chatbot!\n\n' +
                             'If you want to note down something, choose a memory file from the left sidebar, set the mode as Add, and then upload.\n' +
                             'There are three upload types: type-in, upload text file, and upload pdf material. In the first two types, knowledge points will be extracted and stored in the memory file. ' +
                             'In the third type, the file will be first summarized and then knowledge points will be processed likewise. Of course you can manually edit the memory file if you are not satisfied (see below).\n\n' +
                             'If you want to query something, select memory file(s) from the left sidebar and/or `Query LLM` and/or `Query Internet, set the mode as Query, and then type in your query.\n\n' +
                             'You can also manage memory files (add, delete, rename, edit) by clicking the `Manage Memory` button in the left sidebar.\n\n' +
                             'In the right sidebar, you can set parameters for the chatbot and provide feedback.\n\n' +
                             'Enjoy it 😊 Please contact us if you meet any problems.'
         }
    ];
    const [messages, setMessages] = useState(test_msgs);
    const [selectedMemory, setSelectedMemory] = useState([]);
    const [memoryFiles, setMemoryFiles] = useState([]);
    const [showMemoryModal, setShowMemoryModal] = useState(false);
    const [mode, setMode] = useState('Add');
    const [parameters, setParameters] = useState({
        model: 'gpt-3.5-turbo',
        context_size: 100,
        pdf_max_pages: 10,
    });

    const loadingAnimation = (data) => {
        setMessages((prevMessages) => [
            ...prevMessages,
            { type: 'user', text: `${data.mode} Mode: \n\n${data.input}` },
            { type: 'bot', text: 'Loading...' }
        ]);
    }

    const handleSubmit = (data) => {
        // Add user message to the main window
        setMessages((prevMessages) => [
            ...prevMessages.slice(0, -1),
            { type: 'bot', text: `${data.res}` }
        ]);
    };

    const handleFeedback = async (feedback) => {
        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feedback, user_id: 'default_user' })
            });
            const data = await response.json();
            if (!response.ok) {
                alert(data.error);
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
        }
    }

    // Fetch memory files from the server
    const fetchMemoryFiles = async () => {
        try {
            const response = await fetch('/memory?user_id=default_user');
            const data = await response.json();
            setMemoryFiles(data.files);
        } catch (error) {
            console.error('Error fetching memory files:', error);
        }
    };

    useEffect(() => { fetchMemoryFiles(); }, []);

    return (
        <div className="app">
            <Header />
            <div className="main-container">
                <div className="leftsidebar">
                    <div className="memory-header">
                        <h3>Memory</h3>
                        <button onClick={() => setShowMemoryModal(true)} className="manage-button">
                            Manage Memory
                        </button>
                    </div>
                    <br></br>
                    <MemoryManager onMemorySelect={setSelectedMemory} selectedMemory={selectedMemory}
                                   memoryFiles={memoryFiles} mode={mode} />
                </div>
                <div className="content">
                    <MainWindow messages={messages} />
                    <InputArea loading={loadingAnimation} onSubmit={handleSubmit} selectedMemory={selectedMemory}
                               mode={mode} setMode={setMode} parameters={parameters} />
                </div>
                <Sidebar onParameterChange={setParameters} onFeedbackSubmit={handleFeedback} />
            </div>
            {showMemoryModal && (
                <MemoryManagementWindow
                    memoryFiles={memoryFiles}
                    setMemoryFiles={setMemoryFiles}
                    onClose={() => setShowMemoryModal(false)}
                />
            )}
        </div>
    );
}

export default App;
