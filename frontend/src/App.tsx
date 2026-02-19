import { useState, useEffect, type FormEvent } from 'react';
import { searchFlights, ApiError, type SearchResponse, type FlightSummary } from './api';
import './App.css';

// Loading status messages
const LOADING_MESSAGES = [
  'Resolving cities...',
  'Searching flights...',
  'Comparing prices...',
  'Finding best deal...',
];

function App() {
  const [fromCity, setFromCity] = useState('');
  const [toCities, setToCities] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SearchResponse | null>(null);

  // Cycle through loading messages
  useEffect(() => {
    if (!loading) return;

    let index = 0;
    setLoadingMessage(LOADING_MESSAGES[0]);

    const interval = setInterval(() => {
      index = (index + 1) % LOADING_MESSAGES.length;
      setLoadingMessage(LOADING_MESSAGES[index]);
    }, 1500);

    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    const destinations = toCities
      .split(/[,\n]/)
      .map(city => city.trim())
      .filter(city => city.length > 0);

    if (!fromCity.trim()) {
      setError('Please enter a departure city');
      return;
    }

    if (destinations.length === 0) {
      setError('Please enter at least one destination city');
      return;
    }

    setLoading(true);

    try {
      const response = await searchFlights(fromCity.trim(), destinations);
      setResult(response);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatPricePerKm = (price: number): string => {
    return `$${price.toFixed(2)}/km`;
  };

  // Calculate savings percentage compared to worst option
  const getSavingsPercent = (allResults: FlightSummary[]): number => {
    if (allResults.length < 2) return 0;
    const best = allResults[0].price_per_km;
    const worst = allResults[allResults.length - 1].price_per_km;
    if (worst === 0) return 0;
    return Math.round(((worst - best) / worst) * 100);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Flight Optimizer</h1>
        <p className="subtitle">Find the best value flight by price per kilometer</p>
      </header>

      <main className="main">
        <form onSubmit={handleSubmit} className="search-form">
          <div className="form-group">
            <label htmlFor="from-city">From</label>
            <input
              id="from-city"
              type="text"
              value={fromCity}
              onChange={(e) => setFromCity(e.target.value)}
              placeholder="e.g., London"
              disabled={loading}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="to-cities">To (comma-separated)</label>
            <textarea
              id="to-cities"
              value={toCities}
              onChange={(e) => setToCities(e.target.value)}
              placeholder="e.g., Paris, Berlin, Madrid"
              disabled={loading}
              rows={3}
            />
            <span className="hint">Enter multiple cities separated by commas</span>
          </div>

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Searching...' : 'Find Best Flight'}
          </button>
        </form>

        {/* Loading State */}
        {loading && (
          <div className="loading-card">
            <div className="plane-container">
              <div className="plane-path">
                <span className="plane">✈</span>
              </div>
              <div className="clouds">
                <span className="cloud">☁</span>
                <span className="cloud">☁</span>
                <span className="cloud">☁</span>
              </div>
            </div>
            <p className="loading-message">{loadingMessage}</p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="error-message" role="alert">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Results Display */}
        {result && (
          <div className="results-container">
            {/* Best Result Card */}
            <div className="result-card best-result">
              <div className="best-badge">Best Value</div>

              <div className="route-info">
                <span className="route-from">
                  {result.from_city}
                  <span className="country">{result.from_country}</span>
                </span>
                <span className="route-plane">✈</span>
                <span className="route-to">
                  {result.best_destination}
                  <span className="country">{result.to_country}</span>
                </span>
              </div>

              <div className="result-price">
                {formatPricePerKm(result.price_per_km)}
              </div>

              {result.all_results.length > 1 && (
                <div className="savings-badge">
                  {getSavingsPercent(result.all_results)}% cheaper than worst option
                </div>
              )}

              <div className="result-details">
                <div className="detail-item">
                  <span className="detail-label">Total Price</span>
                  <span className="detail-value">${result.total_price.toFixed(2)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Distance</span>
                  <span className="detail-value">{result.distance_km.toFixed(0)} km</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Searched</span>
                  <span className="detail-value">
                    {result.successful_searches} of {result.searched_destinations}
                  </span>
                </div>
              </div>
            </div>

            {/* Other Destinations */}
            {result.all_results.length > 1 && (
              <div className="other-destinations">
                <h3 className="other-destinations-title">Other Options</h3>
                <div className="destinations-list">
                  {result.all_results.filter(r => !r.is_best).map((flight, index) => (
                    <div
                      key={flight.destination}
                      className="destination-card"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <div className="destination-header">
                        <span className="destination-name">
                          {flight.destination}
                          <span className="destination-country">{flight.country}</span>
                        </span>
                        <span className="destination-rank">#{index + 2}</span>
                      </div>
                      <div className="destination-details">
                        <div className="destination-price-per-km">
                          {formatPricePerKm(flight.price_per_km)}
                        </div>
                        <div className="destination-stats">
                          <span>${flight.total_price.toFixed(0)}</span>
                          <span className="separator">•</span>
                          <span>{flight.distance_km.toFixed(0)} km</span>
                        </div>
                      </div>
                      <div
                        className="price-bar"
                        style={{
                          width: `${Math.min(100, (result.all_results[0].price_per_km / flight.price_per_km) * 100)}%`
                        }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Built for B12 Full Stack Engineer Assessment</p>
      </footer>
    </div>
  );
}

export default App;
