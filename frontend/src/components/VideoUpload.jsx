import { useState } from "react";
import "./VideoUpload.css";

function VideoUpload() {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    const handleFileChange = (event) => {
        const selectedFile = event.target.files?.[0];
        if (selectedFile) {
            console.log("File selected:", selectedFile.name);
            setFile(selectedFile);
            setMessage(""); // Clear message when a new file is selected
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
            <h2>Upload a Video</h2>
            <input type="file" accept="video/*" onChange={handleFileChange} />
            <button onClick={uploadVideo} disabled={loading} className={loading ? "disabled-btn" : "upload-btn"}>
                {loading ? "Uploading..." : "Upload"}
            </button>
            {loading && <div className="loader"></div>}
            {message && <p className="message">{message}</p>}
        </div>
    );
}

export default VideoUpload;
