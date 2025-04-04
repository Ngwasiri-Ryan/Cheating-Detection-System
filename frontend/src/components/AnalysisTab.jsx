import React, { useEffect, useState } from 'react';
import { useLogs } from '../context/LogsContext';
import '../styles/AnalysisTab.css';
import NoDataImage from '../assets/analysis.svg';
import DotLoader from './DotLoader';

function AnalysisTab() {
  const { loading, videoDetails, analysisDetails } = useLogs();
  const [currentAnalysis, setCurrentAnalysis] = useState(analysisDetails);

  // Reset analysis details when a new video is uploaded
  useEffect(() => {
    setCurrentAnalysis(null);
  }, [videoDetails]);

  // Update analysis details when available
  useEffect(() => {
    if (analysisDetails) {
      setCurrentAnalysis(analysisDetails);
    }
  }, [analysisDetails]);

  return (
    <div className="analysis-container">
      {/* Loading Indicator */}
      {loading && <div className="loading">
        <DotLoader/>
        <div>Getting Analysis....</div>
       </div>}

      {/* No Analysis Available */}
      {!currentAnalysis && !loading && (
        <div className="no-analysis">
          <img src={NoDataImage} alt="No Analysis" className="no-analysis-img" />
          <p>No analysis available</p>
        </div>
      )}

      {/* Analysis Results Section */}
      {currentAnalysis && (
        <div className="analysis-results">
          <h3>Detection Analysis</h3>

          {/* Statistics Grid */}
          <div className="stats-grid">
            <div className="stat-card">
              <h4>Frames Processed</h4>
              <div className="stat-value">{currentAnalysis.statistics.processing_ratio}</div>
              <div className="stat-subtitle">
                {currentAnalysis.statistics.processed_frames}/{currentAnalysis.statistics.total_frames} frames
              </div>
            </div>

            <div className="stat-card">
              <h4>Face Detection</h4>
              <div className="stat-value">{currentAnalysis.statistics.face_detection_rate}</div>
              <div className="stat-subtitle">
                {currentAnalysis.raw_counts.face_detections} detections
              </div>
            </div>

            <div className="stat-card">
              <h4>Lookaway Ratio</h4>
              <div className="stat-value">{currentAnalysis.statistics.lookaway_ratio}</div>
              <div className="stat-subtitle">
                {currentAnalysis.raw_counts.lookaway_count} lookaways
              </div>
            </div>

            <div className="stat-card">
              <h4>Multiple Faces</h4>
              <div className="stat-value">
                {currentAnalysis.statistics.multiple_faces_detected ? "Yes" : "No"}
              </div>
            </div>
          </div>

          {/* Raw Data (expandable) */}
          <details className="raw-data">
            <summary>View Technical Details</summary>
            <pre>{JSON.stringify(currentAnalysis.raw_counts, null, 2)}</pre>
          </details>
        </div>
      )}
    </div>
  );
}

export default AnalysisTab;
