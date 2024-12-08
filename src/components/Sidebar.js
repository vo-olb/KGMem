import React, { useState } from 'react';

function Sidebar({ onParameterChange, onFeedbackSubmit }) {
    const [parameters, setParameters] = useState({
        model: 'gpt-3.5-turbo',
        context_size: 100,
        pdf_max_pages: 10,
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
            <h4>Settings</h4>
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
            <div className="parameter">
                <label htmlFor="context-size">Context Size (Number of Lines for Each Memory File to Consider):</label>
                <input
                    id="context-size"
                    type="number"
                    value={parameters.context_size}
                    onChange={(e) => handleParameterChange('context_size', parseInt(e.target.value, 10))}
                />
            </div>
            <div className="parameter">
                <label htmlFor="pdf-max-pages">Max Pages of PDF to Read:</label>
                <input
                    id="pdf-max-pages"
                    type="number"
                    value={parameters.pdf_max_pages}
                    onChange={(e) => handleParameterChange('pdf_max_pages', parseInt(e.target.value, 10))}
                />
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