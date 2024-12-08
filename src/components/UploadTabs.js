import React from 'react';

function UploadTabs({ selectedTab, onSelect }) {
    const tabs = ['type-in', 'upload', 'material'];

    return (
        <div className="tabs-container">
            {tabs.map((tab) => (
                <button
                    key={tab}
                    onClick={() => onSelect(tab)}
                    className={`tab-button ${selectedTab === tab ? 'active-tab' : ''}`}
                >
                    {tab}
                </button>
            ))}
        </div>
    );
}

export default UploadTabs;