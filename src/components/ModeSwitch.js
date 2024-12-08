import React from 'react';

function ModeSwitch({ mode, onChange }) {
    return (
        <div className="mode-switch">
            <button onClick={() => onChange(mode === 'Add' ? 'Query' : 'Add')} className="switch-button">
                Switch Mode
            </button>
        </div>
    );
}

export default ModeSwitch;