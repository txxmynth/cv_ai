import React, { useState } from 'react';
import './TextBubble.css';

const TextBubble = ({ fetchData }) => {
    const [inputText, setInputText] = useState("");

    const handleChange = (event) => {
        setInputText(event.target.value);
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            fetchData(inputText);
            setInputText("");
        }
    };

    const handleClick = () => {
        fetchData(inputText);
        setInputText(""); 
    };

    return (
        <div className='bubble'>
            <input
                className='text'
                type="text"
                value={inputText}
                onChange={handleChange}
                onKeyDown={handleKeyDown} // Add the onKeyDown event handler
                placeholder="Type your message here"
            />
            <button type="button" className="send" onClick={handleClick}>Send</button>
        </div>
    );
};

export default TextBubble;
