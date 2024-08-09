import React, { useState } from 'react';
import Box from './Box.js';
import TextBubble from './TextBubble.js';
import './App.css';

const App = () => {
    const [aiResponse, setAiResponse] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchAIResponse = async (query) => {
        setLoading(true);
        try {
            const response = await fetch('/get_response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            if (response.ok) {
                setAiResponse(data.response);
            } else {
                throw new Error(data.error || 'Something went wrong');
            }
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };
    return (
        <div className="App">
            <div>
                <Box data={aiResponse} loading={loading}/>
            </div>
            <div>
                <TextBubble fetchData={fetchAIResponse} />
            </div>
        </div>
    );
};

export default App;
