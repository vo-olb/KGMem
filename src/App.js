import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MainWindow from './components/MainWindow';
import InputArea from './components/InputArea';
import MemoryManager from './components/MemoryManager';
import MemoryManagementWindow from './components/MemoryManagementWindow';
import Sidebar from './components/Sidebar';

function App() {
    const instructions = 
    '## Welcome to the Chatbot!\n' +
    '**📝 Note-Taking:**\n' +
    '• To record something, choose memory file(s) from the left sidebar, set the mode to ➕ **Add**, and ⬆️ **submit** your content. \n' +
    '• There are three upload types:\n' +
    '&emsp;1️⃣ **Type-In:** Enter your text manually. \n'+
    '&emsp;2️⃣ **Text File:** Upload a .txt file. \n' +
    '&emsp;3️⃣ **PDF File:** Upload a .pdf file. \n' +
    '• For **type-in** and **text file** uploads, [GraphRAG](https://microsoft.github.io/graphrag/#solution-accelerator) will extract all possible entities and relationships to construct a **knowledge graph**. This is suitable for short inputs such as your notes from lectures, meetings, or experiments.\n' +
    '• For **PDF uploads**, the file will be **summarized** for you to have a quick grasp with a **focus** determined by you. The **knowledge graph** will be extracted similarly, but tailored to your chosen **focus**. This is suitable for long research papers. \n\n' +
    '**🔍 Querying:**\n' +
    '• To search for information, select memory file(s) from the left sidebar, and/or choose **Query LLM 🤖** and/or **Query Internet 🛜**. \n' +
    '• Set the mode to **❓ Query**, type in your query, and **⬆️ submit** your content. \n\n' +
    '**🛠️ Manage Memory:**\n' +
    '• You can **add, delete, rename, or visualize** memory files by clicking the **Manage Memory** button in the left sidebar. \n\n' +
    '**⚙️ Settings & Feedback:**\n' +
    '• Use the right sidebar to set chatbot parameters and provide feedback 🙋. \n\n' +
    '**✨ Try it out!**\n' +
    'If you encounter any issues, please contact us for assistance.'

    const welcome_msg = [
        { type: 'bot', text: instructions}
    ];
    const [messages, setMessages] = useState(welcome_msg);
    const [selectedMemory, setSelectedMemory] = useState([]);
    const [memoryFiles, setMemoryFiles] = useState([]);
    const [showMemoryModal, setShowMemoryModal] = useState(false);
    const [mode, setMode] = useState('Add');
    const [selectedTab, setSelectedTab] = useState('type-in'); // For add mode only
    const [knowledgeType, setKnowledgeType] = useState('');
    const [entityType, setEntityType] = useState('');
    const [parameters, setParameters] = useState({
        model: 'gpt-3.5-turbo',
    });

    const loadingAnimation = (data) => {
        const typelist = `\n\n**Chosen Knowledge Type:** ${knowledgeType}\n**Chosen Entity Type:** ${entityType}`;
        setMessages((prevMessages) => [
            ...prevMessages,
            { type: 'user', text: `**${data.mode} Mode:** \n\n${data.input}${mode === 'Add' && selectedTab === 'material' ? typelist : ''}` },
            { type: 'bot', text: 'Loading...' }
        ]);
    }

    const handleSubmit = (data) => {
        // Add user message to the main window
        setMessages((prevMessages) => [
            ...prevMessages.slice(0, -1),
            ...data.res.map((text) => ({ type: 'bot', text })),
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
                               mode={mode} setMode={setMode} selectedTab={selectedTab} setSelectedTab={setSelectedTab} 
                               knowledgeType={knowledgeType} setKnowledgeType={setKnowledgeType} entityType={entityType}
                               setEntityType={setEntityType} parameters={parameters}/>
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
