import React from "react";
import Header from "../components/Header";
import Menu from "../components/Menu";
import History from "../components/History";
import VideoRecorder from "../components/VideoRecorder";
import VideoUpload from "../components/VideoUpload";
import Logs from "../components/Logs";
import '../styles/Home.css'


const Home = () => {
  return (
    <>
      {/* <VideoRecorder />  */}
    <div className="parent">
   <div className="div1">
    <Header/>
   </div>
   <div className="div2">
    <Menu/>
   </div>
   <div className="div3">
    <VideoUpload/>
   </div>
   <div className="div4">
    <History/>
   </div>
   <div className="div5">
    <Logs/>
   </div>
</div>
    
   </>
  );
};

export default Home;
