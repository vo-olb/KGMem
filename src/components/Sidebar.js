import React, { useState } from 'react';

function Sidebar({ onParameterChange, onFeedbackSubmit }) {
    const [parameters, setParameters] = useState({
        model: 'gpt-3.5-turbo',
    });
    const [feedback, setFeedback] = useState('');

    const handleParameterChange = (key, value) => {
        const updatedParameters = { ...parameters, [key]: value };
        setParameters(updatedParameters);
        onParameterChange(updatedParameters); // Notify parent of changes
    };

    const handleSubmitFeedback = () => {
        onFeedbackSubmit(feedback);
        setFeedback('');
        alert('Thank you for your feedback!');
    };

    return (
        <div className="rightsidebar">
            <div className="rightsidebar-header">
                <h4>Settings</h4>
                <div className='github-link'>
                    <a
                        href="https://github.com/vo-olb/KGMem"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        <img
                            src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg"
                            alt="GitHub"
                            className="github-icon"
                        />
                    </a>
                </div>
            </div>
            <div className="parameter">
                <label htmlFor="model">Model:</label>
                <select
                    id="model"
                    value={parameters.model}
                    onChange={(e) => handleParameterChange('model', e.target.value)}
                >
                    <option value="gpt-3.5-turbo">GPT-3.5</option>
                    <option value="gpt-4">GPT-4</option>
                </select>
            </div>
            <br></br>
            <h4>Feedback</h4>
            <textarea
                placeholder="Share your thoughts..."
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
            />
            <button onClick={handleSubmitFeedback}>Submit</button>
        </div>
    );
}

export default Sidebar;