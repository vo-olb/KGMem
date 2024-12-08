import React, { useState } from 'react';
import ModeSwitch from './ModeSwitch';
import UploadTabs from './UploadTabs';

function InputArea({ loading, onSubmit, selectedMemory, mode, setMode, parameters }) {
    const [selectedTab, setSelectedTab] = useState('type-in'); // For add mode only
    const [input, setInput] = useState('');
    const [file, setFile] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setInput(selectedFile.name);
        }
    }

    const handleSubmit = async () => {
        if (isSubmitting) return;
        setIsSubmitting(true);

        const formData = new FormData();
        formData.append('mode', mode);
        formData.append('selectedTab', selectedTab);
        formData.append('parameters', JSON.stringify(parameters));
        
        if (selectedMemory.length > 0) {
            formData.append('selectedMemory', selectedMemory);
        } else {
            alert('Please select a memory.');
            setIsSubmitting(false);
            return;
        }

        if (mode === 'Add' && selectedTab !== 'type-in') {
            if (file) {
                formData.append('file', file);
            } else {
                alert('Please select a file to upload.');
                setIsSubmitting(false);
                return;
            }
        }

        if (input.trim()) {
            formData.append('input', input);
        } else {
            alert('Please enter a prompt.');
            setIsSubmitting(false);
            return;
        }

        loading({ mode, input });

        try {
            const response = await fetch('/process_request?user_id=default_user', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            onSubmit({ res: result.response });
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setIsSubmitting(false);
        }
        setInput('');
        setFile(null);
    };

    return (
        <div className="input-area">
            <div className="switch-mode-container">
                <ModeSwitch mode={mode} onChange={setMode} />
                <div className="current-mode">{mode} Mode</div>
            </div>
            <div className="input-and-type-container">
                {mode === 'Add' && <UploadTabs selectedTab={selectedTab} onSelect={setSelectedTab} />}
                <div className="input-container">
                    {selectedTab === 'type-in' || mode === 'Query' ? (
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Enter your prompt or upload file..."
                            className="input-field"
                            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                            disabled={isSubmitting}
                        />
                    ) : (
                        <input
                            type="file"
                            accept={selectedTab === 'upload' ? '.txt' : '.pdf'}
                            onChange={handleFileChange}
                            disabled={isSubmitting}
                        />
                    )}
                    <button onClick={handleSubmit} className="upload-button" disabled={isSubmitting}>⬆</button>
                </div>
            </div>
        </div>
    );
}

export default InputArea;