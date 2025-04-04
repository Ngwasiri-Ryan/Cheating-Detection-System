import React from "react";
import { useLogs } from "../context/LogsContext";
import '../styles/Logs.css'


function Logs() {
    const { message, loading } = useLogs(); // Get data from context
    const { videoDetails } = useLogs();

    return (
        <div className="logs-container">
            <div>
            {videoDetails ? (
                <div className='videoDetails'>
                    <div className='videoDetail'><strong>Name: </strong>{videoDetails.name}</div>
                    <div className='videoDetail'><strong>Time: </strong>{videoDetails.duration}</div>
                    <div className='videoDetail'><strong>Size: </strong>{videoDetails.size}</div>
                   
                </div>
            ) : (
                <p>No video uploaded yet.</p>
            )}
            </div>
            {loading && <div className="loader"></div>}
            {message && <p className="message">{message}</p>}
        </div>
    );
}

export default Logs;
