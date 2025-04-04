import React from 'react';

function SavedResultsTab() {
  // You would fetch saved results from your backend or context here
  const savedResults = []; // Placeholder for actual data

  return (
    <div className="saved-results-container">
      <h3>Previously Saved Results</h3>
      {savedResults.length > 0 ? (
        <ul className="results-list">
          {savedResults.map((result, index) => (
            <li key={index} className="result-item">
              <div className="result-meta">
                <span className="result-date">{result.date}</span>
                <span className={`result-status ${result.cheatingDetected ? 'detected' : 'clean'}`}>
                  {result.cheatingDetected ? 'Cheating Detected' : 'Clean Session'}
                </span>
              </div>
              <button className="view-details-btn">View Details</button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="no-results">No saved results yet.</p>
      )}
    </div>
  );
}

export default SavedResultsTab;