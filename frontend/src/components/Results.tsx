import React from "react";

interface ResultsProps {
  cheatingDetected: boolean | null;
}

const Results: React.FC<ResultsProps> = ({ cheatingDetected }) => {
  return (
    <div>
      <h2>Analysis Result</h2>
      {cheatingDetected === null ? (
        <p>Processing video...</p>
      ) : cheatingDetected ? (
        <p style={{ color: "red", fontWeight: "bold" }}>⚠️ Cheating Detected!</p>
      ) : (
        <p style={{ color: "green", fontWeight: "bold" }}>✅ No Cheating Detected</p>
      )}
    </div>
  );
};

export default Results;
