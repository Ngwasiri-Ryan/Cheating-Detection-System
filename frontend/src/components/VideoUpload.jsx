import { useState, useRef } from "react";
import { useLogs } from "../context/LogsContext";
import "../styles/VideoUpload.css";
import placeholder from "../assets/placeholder.svg";

function VideoUpload() {
    const [file, setFile] = useState(null);
    const [videoURL, setVideoURL] = useState(null);
    const videoRef = useRef(null);
    const { setMessage, setLoading, setVideoDetails } = useLogs();

    const handleFileChange = (event) => {
        const selectedFile = event.target.files?.[0];
        if (selectedFile) {
            console.log("File selected:", selectedFile.name);
            setFile(selectedFile);
            setMessage(""); // Clear previous message
            
            // Revoke previous object URL
            if (videoURL) {
                URL.revokeObjectURL(videoURL);
            }

            const url = URL.createObjectURL(selectedFile);
            setVideoURL(url);

            setTimeout(() => {
                const videoElement = videoRef.current;
                if (videoElement) {
                    videoElement.load();

                    // Extract metadata once the video is loaded
                    videoElement.onloadedmetadata = () => {
                        const videoSize = (selectedFile.size / (1024 * 1024)).toFixed(2) + " MB"; // Convert bytes to MB
                        setVideoDetails({
                            name: selectedFile.name,
                            duration: videoElement.duration.toFixed(2) + " seconds",
                            size: videoSize,
                        });
                    };
                }
            }, 0);
        }
    };

    const uploadVideo = async () => {
        if (!file) {
            console.warn("⚠️ No file selected");
            setMessage("⚠️ Please select a video file.");
            return;
        }

        console.log("Uploading video:", file.name);
        setLoading(true);
        setMessage("Uploading...");

        const formData = new FormData();
        formData.append("video", file);

        try {
            console.log("Sending request to backend...");
            const response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Failed to upload video.");
            }

            const result = await response.json();
            console.log("Response received:", result);
            setMessage(result.cheating_detected ? "🚨 Cheating Detected!" : "✅ No Cheating Detected.");
        } catch (error) {
            console.error("Error uploading video:", error);
            setMessage("❌ Upload failed. Please try again.");
        } finally {
            console.log("Upload process completed.");
            setLoading(false);
        }
    };

    return (
        <div className="upload-container">
            <div className="heading">Upload Video to Scan</div>
            <label className="custom-file-upload">
                <input type="file" accept="video/*" onChange={handleFileChange} />
                📁 Choose Video
            </label>

            <div className="media-preview">
                {videoURL ? (
                    <video id="video-player" ref={videoRef} controls width="100%">
                        <source src={videoURL} type="video/mp4" />
                        Your browser does not support the video tag.
                    </video>
                ) : (
                    <img src={placeholder} alt="No Video Selected" className="placeholder-image" />
                )}
            </div>

            <button onClick={uploadVideo} className="upload-btn">
               Scan Video
            </button>
        </div>
    );
}

export default VideoUpload;
