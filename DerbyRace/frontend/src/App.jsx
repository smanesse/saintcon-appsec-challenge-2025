import { useState, useEffect } from 'react';
import './App.css';

const API_BASE = '/api/derby';
const TRACK_LENGTH = 500;

function App() {
  const [horseName, setHorseName] = useState('');
  const [gameState, setGameState] = useState({
    isSetup: false,
    lastRoll: 5,
    previousRoll: null,
    timingBonus: 0,
    isWinner: false,
    horses: [],
    raceOver: false,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const apiCall = async (endpoint, options) => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE}/${endpoint}`, options);
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.message || `HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      setError(err.message || 'Connection error');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const setupHorse = async () => {
    if (!horseName.trim()) {
      setError('Please enter a horse name');
      return;
    }
    const data = await apiCall('setup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ horseName }),
    });

    if (data?.success) {
      setGameState({
        isSetup: true,
        lastRoll: data.last_roll || 5,
        previousRoll: null,
        timingBonus: 0,
        horses: data.horses || [],
        isWinner: false,
        raceOver: false,
      });
    }
  };
  
  const dashHorse = async () => {
    const data = await apiCall('dash', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });

    if (data?.success) {
      setGameState(prev => ({
        ...prev,
        horses: data.horses || [],
        previousRoll: prev.lastRoll,
        lastRoll: data.last_roll || prev.lastRoll,
        timingBonus: data.timing_bonus || 0,
        isWinner: data.winner || false,
        raceOver: data.race_over || false,
      }));
    }
  };

  const resetGame = () => {
    setHorseName('');
    setGameState({
        isSetup: false,
        lastRoll: 5,
        previousRoll: null,
        timingBonus: 0,
        isWinner: false,
        horses: [],
        raceOver: false,
    });
    setError('');
  }

  const renderRaceResult = () => {
    if (!gameState.raceOver) return null;
    
    // Calculate final standings
    const standings = gameState.horses
      .map((horse, index) => ({ ...horse, originalIndex: index }))
      .sort((a, b) => b.position - a.position);
    
    const playerStanding = standings.findIndex(h => h.is_player) + 1;
    
    const getPlacementSuffix = (place) => {
      if (place === 1) return 'st';
      if (place === 2) return 'nd';
      if (place === 3) return 'rd';
      return 'th';
    };
    
    return (
      <div className="race-result-overlay">
        <div className="race-result-modal">
          <h2>{gameState.isWinner ? '🎉 You Won! 🎉' : '🏁 Race Over 🏁'}</h2>
          <p>{gameState.isWinner ? `Congratulations! Your horse crossed the finish line first!` : `You finished in ${playerStanding}${getPlacementSuffix(playerStanding)} place!`}</p>
          {gameState.previousRoll && (
            <p className="final-roll">Your Final Roll: <strong>{gameState.previousRoll}</strong></p>
          )}
          
          <div className="final-standings">
            <h3>Final Standings</h3>
            <div className="standings-list">
              {standings.map((horse, index) => (
                <div key={index} className={`standing-item ${horse.is_player ? 'player-standing' : ''}`}>
                  <span className="placement">{index + 1}{getPlacementSuffix(index + 1)}</span>
                  <span className="horse-name-standing">{horse.name}</span>
                  <span className="horse-position-standing">{horse.position}</span>
                </div>
              ))}
            </div>
          </div>
          
          <button onClick={resetGame} className="primary-button">
            Play Again
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Golden Derby Classic</h1>
        <p>A Game of Speed and... Precision Engineering.</p>
      </header>
      
      {renderRaceResult()}

      <main className="main">
        {!gameState.isSetup ? (
          <div className="setup-section">
            <div className="setup-content">
              <div className="setup-form">
                <h2>Name Your Champion</h2>
                <div className="input-group">
                  <input
                    type="text"
                    value={horseName}
                    onChange={(e) => setHorseName(e.target.value)}
                    placeholder="Enter horse name"
                    maxLength={32}
                    disabled={loading}
                    onKeyPress={(e) => e.key === 'Enter' && setupHorse()}
                  />
                  <button 
                    onClick={setupHorse} 
                    disabled={loading || !horseName.trim()}
                    className="primary-button"
                  >
                    {loading ? 'Starting...' : 'Start Race'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="game-section">
            <div className="race-track-container">
                <div className="dice-display">
                  <div className="dice-info">
                    {gameState.previousRoll ? (
                      <div className="roll-used">
                        <span className="roll-label">Roll Used:</span>
                        <span className="roll-value">{gameState.previousRoll}</span>
                      </div>
                    ) : null}
                    <div className="next-roll">
                      <span className="roll-label">Next Roll:</span>
                      <span className="roll-value">{gameState.lastRoll}</span>
                    </div>
                    <div className="timing-display">
                      <span className="roll-label">Timing Bonus:</span>
                      <div className="timing-bar">
                        <div
                          className="timing-fill"
                          style={{
                            height: `${Math.max(0, Math.min(100, (gameState.timingBonus / 10) * 100))}%`,
                            background: `hsl(${(gameState.timingBonus / 10) * 120}, 70%, 50%)`
                          }}
                        ></div>
                        <span className="timing-value">{gameState.timingBonus}</span>
                      </div>
                    </div>
                  </div>
                </div>
              <div className="race-track">
                {gameState.horses.map((horse, index) => (
                  <div key={index} className="race-lane">
                    <div className="lane-label">
                      <span className="horse-name">{horse.name}</span>
                      <span className="horse-position">{horse.position}/{TRACK_LENGTH}</span>
                    </div>
                    <div className="lane">
                      <div 
                        className={`horse ${horse.is_player ? 'player-horse' : ''}`}
                        style={{ 
                          left: `${Math.min((horse.position / TRACK_LENGTH) * 88, 88)}%`
                        }}
                      >
                        <img src="/Horse.png" alt="Horse" className="horse-image" />
                      </div>
                      <div className="finish-line"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="race-controls">
              <button 
                onClick={dashHorse}
                disabled={loading || gameState.raceOver}
                className="dash-button"
              >
                {loading ? 'Dashing...' : 'DASH!'}
              </button>
              <button 
                onClick={resetGame} 
                disabled={loading}
                className="secondary-button"
              >
                {loading ? 'Resetting...' : 'New Race'}
              </button>
            </div>
          </div>
        )}
        {error && <div className="error-banner">{error}</div>}
      </main>
    </div>
  );
}

export default App;
