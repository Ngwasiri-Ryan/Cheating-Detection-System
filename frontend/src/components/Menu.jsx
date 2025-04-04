import React, { useState } from 'react';
import AnalysisTab from './AnalysisTab';
import SavedResultsTab from './SavedResultsTab';
import '../styles/Tabs.css';

function Menu() {
  const [activeTab, setActiveTab] = useState('analysis');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'analysis':
        return <AnalysisTab />;
      case 'saved':
        return <SavedResultsTab />;
      default:
        return <AnalysisTab />;
    }
  };

  return (
    <div className="tabs-container">
      <div className="tabs-header">
        <button
          className={`tab-button ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          Analysis
        </button>
        <button
          className={`tab-button ${activeTab === 'saved' ? 'active' : ''}`}
          onClick={() => setActiveTab('saved')}
        >
          Saved Results
        </button>
      </div>
      
      <div className="tab-content">
        {renderTabContent()}
      </div>
    </div>
  );
}

export default Menu;