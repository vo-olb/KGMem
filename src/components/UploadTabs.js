import React from 'react';

function UploadTabs({ selectedTab, onSelect }) {
    const tabs = ['type-in', 'upload', 'material'];

    const tabLabels = {
        'type-in': 'Type-In',
        'upload': 'Text File',
        'material': 'PDF File'
    };

    return (
        <div className="tabs-container">
            {tabs.map((tab) => (
                <button
                    key={tab}
                    onClick={() => onSelect(tab)}
                    className={`tab-button ${selectedTab === tab ? 'active-tab' : ''}`}
                >
                    {tabLabels[tab]}
                </button>
            ))}
        </div>
    );
}

export default UploadTabs;