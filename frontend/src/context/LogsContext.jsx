import { createContext, useContext, useState } from "react";

const LogsContext = createContext();

export const LogsProvider = ({ children }) => {
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const [videoDetails, setVideoDetails] = useState(null);

    return (
        <LogsContext.Provider value={{ message, setMessage, loading, setLoading, videoDetails, setVideoDetails }}>
            {children}
        </LogsContext.Provider>
    );
};

export const useLogs = () => useContext(LogsContext);
