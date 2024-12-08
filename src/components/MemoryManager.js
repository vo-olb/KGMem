import {React, useState} from 'react';

function MemoryManager({ onMemorySelect, selectedMemory, memoryFiles, mode }) {

    const [activeQueries, setActiveQueries] = useState({ LLM: false, Internet: false });

    const toggleQuery = (query) => {
        const newActiveQueries = { ...activeQueries, [query]: !activeQueries[query] };

        if (newActiveQueries[query]) {
            onMemorySelect([...selectedMemory, `%${query}%`]);
        } else {
            onMemorySelect(selectedMemory.filter((file) => file !== `%${query}%`));
        }

        setActiveQueries(newActiveQueries);
    };

    return (
        <div className="memory-manager">
            <label htmlFor='memory-selection'>Select Memories:</label>
            <select
                id="memory-selection"
                multiple
                onChange={(e) => {
                    const selectedOptions = Array.from(e.target.selectedOptions).map(
                        (option) => option.value
                    );
                    onMemorySelect([...selectedOptions, 
                                    ...selectedMemory.filter((file) => file === '%LLM%' || file === '%Internet%')
                    ]); // Update parent
                }}
                className="memory-selection"
            >
                {memoryFiles.map((file) => (
                    <option key={file} value={file}>
                        {file}
                    </option>
                ))}
            </select>
            {mode === 'Query' && (
                <div className="query-buttons">
                <button
                    className={`query-button ${activeQueries.LLM ? 'active' : ''}`}
                    onClick={() => toggleQuery('LLM')}
                >
                    Query LLM
                </button>
                <button
                    className={`query-button ${activeQueries.Internet ? 'active' : ''}`}
                    onClick={() => toggleQuery('Internet')}
                >
                    Query Internet
                </button>
            </div>
            )}
        </div>
    );
}

export default MemoryManager;