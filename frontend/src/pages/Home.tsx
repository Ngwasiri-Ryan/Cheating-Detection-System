import React from "react";
import VideoRecorder from "../components/VideoRecorder";
import VideoUpload from "../components/VideoUpload";

const Home: React.FC = () => {
  return (
    <div>
      <h1>AI Cheating Detection</h1>
      {/* <VideoRecorder />  */}
      <VideoUpload/>
    </div>
  );
};

export default Home;
