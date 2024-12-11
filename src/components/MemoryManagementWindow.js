import React, { useState } from 'react';

function MemoryManagementWindow({ memoryFiles, setMemoryFiles, onClose }) {
    const [newFileName, setNewFileName] = useState('');
    const [renameTarget, setRenameTarget] = useState();
    const [renameValue, setRenameValue] = useState('');

    const checkFileName = (fileName) => { // Adjust as needed
        if (!fileName) {
            alert('Invalid file name (empty).');
            return false;
        }
        if (fileName.includes(',')) { // TODO: Add more checks as needed, such as /, \, etc.
            alert("Invalid file name (containing comma).")
            return false;
        }
        return true;
    }

    const onCreate = async (fileName) => {
        if (!checkFileName(fileName)) return;
        try {
            const response = await fetch('/memory?user_id=default_user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify({ file_name: fileName }),
            });
            if (response.ok) {
                setMemoryFiles([...memoryFiles, fileName]);
            } else {
                const res = await response.json();
                alert(res.error);
            }
        } catch (error) {
            console.error('Error creating memory:', error);
        }
    }

    const onDelete = async (fileName) => {
        if (!window.confirm(`Are you sure you want to delete ${fileName}?`)) {
            return;
        }
        try {
            const response = await fetch('/memory?user_id=default_user', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify({ file_name: fileName }),
            });
            if (response.ok) {
                setMemoryFiles(memoryFiles.filter((file) => file !== fileName));
            } else {
                const res = await response.json();
                alert(res.error);
            }
        } catch (error) {
            console.error('Error deleting memory:', error);
        }
    }

    const onRename = async (fileName, newFileName) => {
        if (!checkFileName(newFileName)) return;
        try {
            const response = await fetch('/memory?user_id=default_user', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify({ old_file_name: fileName, new_file_name: newFileName }),
            });
            if (response.ok) {
                setMemoryFiles(memoryFiles.map((file) => (file === fileName ? newFileName : file)));
            } else {
                const res = await response.json();
                alert(res.error);
            }
        } catch (error) {
            console.error('Error renaming memory:', error);
        }
    };

    const onVisual = async (fileName) => {
        try {
            const response = await fetch('/visual?user_id=default_user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify({ fileName }),
            });
            if (!response.ok) {
                const res = await response.json();
                alert(res.error);
            } else {
                const url = '/visualizer/' + 'default_user' + '/build/index.html';
                window.location.href = url;
            }
        } catch (error) {
            console.error('Error visualizing memory:', error);
        }
    }
        

    return (
        <div className="modal">
            <div className="modal-content">
                <h4>Manage Memories</h4>
                {/* Create New Memory */}
                <div>
                    <h5>Create New Memory</h5>
                    <input
                        type="text"
                        value={newFileName}
                        onChange={(e) => setNewFileName(e.target.value)}
                        placeholder="New memory name"
                    />
                    <button onClick={() => { onCreate(newFileName); setNewFileName(''); }}>
                        Create
                    </button>
                </div>
                {/* Existing Memories */}
                <div>
                    <h5>Existing Memories</h5>
                    <ul>
                        {memoryFiles.map((file) => (
                            <li key={file}>
                                <span style={{ flexGrow: 1 }}>{file}</span>
                                <button onClick={() => onDelete(file)}>Delete</button>
                                {renameTarget === file ? (
                                    <>
                                        <input
                                            type="text"
                                            value={renameValue}
                                            onChange={(e) => setRenameValue(e.target.value)}
                                            placeholder="New name"
                                        />
                                        <button
                                            onClick={() => {
                                                onRename(renameTarget, renameValue);
                                                setRenameTarget('');
                                                setRenameValue('');
                                            }}
                                        >
                                            Rename
                                        </button>
                                    </>) : (
                                        <button onClick={() => setRenameTarget(file)}>Rename</button>
                                )}
                                <button onClick={() => onVisual(file)}>Visualize</button>
                            </li>
                        ))}
                    </ul>
                </div>
                <button
                    onClick={() => {
                        setNewFileName('');
                        setRenameTarget('');
                        setRenameValue('');
                        onClose();
                    }}
                    className="close-button"
                >
                    Close
                </button>
            </div>
        </div>
    );
}

export default MemoryManagementWindow;