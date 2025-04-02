import React, { useState, useEffect } from 'react';
import Home from './pages/Home';
import './styles/Home.css';
import { LogsProvider } from './context/LogsContext';
import Loader from './components/Loader';

function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 5000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <LogsProvider>
      <div className='body'>
        {loading ? <Loader /> : <Home />}
      </div>
    </LogsProvider>
  );
}

export default App;
