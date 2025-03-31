import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";
import Results from "./Results";

const VideoRecorder: React.FC = () => {
  const webcamRef = useRef<Webcam>(null);
  const [recording, setRecording] = useState(false);
  const [cheatingDetected, setCheatingDetected] = useState<boolean | null>(null);

  const startRecording = () => {
    setRecording(true);
    setCheatingDetected(null); // Reset previous results
  };

  const stopRecording = () => {
    setRecording(false);
    if (webcamRef.current) {
      const videoData = webcamRef.current.getScreenshot();
      if (videoData) {
        sendToBackend(videoData);
      }
    }
  };

  const sendToBackend = async (video: any) => {
    const formData = new FormData();
    formData.append("video", video);

    try {
      const response = await axios.post("http://localhost:5000/upload", formData);
      setCheatingDetected(response.data.cheating_detected);
    } catch (error) {
      console.error("Error uploading video:", error);
    }
  };

  return (
    <div>
      <Webcam ref={webcamRef} screenshotFormat="image/jpeg" />
      {recording ? (
        <button onClick={stopRecording}>Stop Recording</button>
      ) : (
        <button onClick={startRecording}>Start Recording</button>
      )}

      {/* Show Results after processing */}
      <Results cheatingDetected={cheatingDetected} />
    </div>
  );
};

export default VideoRecorder;
