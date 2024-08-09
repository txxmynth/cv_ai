import React from 'react';
import './Box.css'

const Box = ({ data, loading }) => {
    return (
        <div className="box">
            {loading ? "Loading..." : (data ? data : "Hello, how may I assist you?")}
        </div>
    );
};

export default Box;
