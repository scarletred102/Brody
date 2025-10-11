import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [dayPreparation, setDayPreparation] = useState(null);
  const [loading, setLoading] = useState(false);

  const prepareDayClick = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/prepare-day');
      const data = await response.json();
      setDayPreparation(data);
    } catch (error) {
      console.error('Error fetching day preparation:', error);
      // Use mock data if backend is not running
      setDayPreparation({
        date: new Date().toISOString(),
        meetings: [],
        tasks: [],
        summary: "Brody is ready to help! (Backend not connected)"
      });
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 Brody</h1>
        <p className="tagline">Your Proactive Multi-Agent AI Hub</p>
      </header>

      <main className="App-main">
        <div className="hero-section">
          <h2>Prepare Your Day in One Click</h2>
          <button 
            className="prepare-button"
            onClick={prepareDayClick}
            disabled={loading}
          >
            {loading ? 'Preparing...' : '✨ Prepare My Day'}
          </button>
        </div>

        {dayPreparation && (
          <div className="preparation-results">
            <h3>📋 Your Day Summary</h3>
            <div className="summary-card">
              <p>{dayPreparation.summary}</p>
              
              {dayPreparation.meetings && dayPreparation.meetings.length > 0 && (
                <div className="section">
                  <h4>📅 Meetings</h4>
                  <ul>
                    {dayPreparation.meetings.map((meeting, idx) => (
                      <li key={idx}>{meeting.title}</li>
                    ))}
                  </ul>
                </div>
              )}

              {dayPreparation.tasks && dayPreparation.tasks.length > 0 && (
                <div className="section">
                  <h4>✅ Tasks</h4>
                  <ul>
                    {dayPreparation.tasks.map((task, idx) => (
                      <li key={idx}>{task.title}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="features">
          <h3>What Brody Does</h3>
          <div className="feature-grid">
            <div className="feature-card">
              <h4>🚀 Proactive Intelligence</h4>
              <p>Anticipates your needs before you ask</p>
            </div>
            <div className="feature-card">
              <h4>📧 Unified Workspace</h4>
              <p>Email, tasks, and calendar in one place</p>
            </div>
            <div className="feature-card">
              <h4>🤝 AI-to-AI Collaboration</h4>
              <p>Multiple agents working together seamlessly</p>
            </div>
            <div className="feature-card">
              <h4>⚡ Save 5-7 Hours Weekly</h4>
              <p>Automate repetitive tasks and context switching</p>
            </div>
          </div>
        </div>
      </main>

      <footer className="App-footer">
        <p>Brody v0.1.0 - MVP Phase</p>
      </footer>
    </div>
  );
}

export default App;
