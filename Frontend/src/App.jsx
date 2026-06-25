import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [jobDescription, setJobDescription] = useState("");
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Change this to your deployed backend URL later
  const API_URL =
    import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

  const rankCandidates = async () => {
    try {
      setLoading(true);
      setError("");
      setResults([]);

      const response = await axios.post(
        `${API_URL}/rank_candidates`,
        {
          job_description: jobDescription,
          top_k: Number(topK),
        },
        {
          timeout: 10000,
        }
      );

      if (response.data?.top_candidates) {
        setResults(response.data.top_candidates);
      } else {
        setError("No candidates returned from backend.");
      }
    } catch (err) {
      console.error(err);

      if (err.response) {
        setError(
          `Backend Error ${err.response.status}: ${
            err.response.data?.error || JSON.stringify(err.response.data)
          }`
        );
      } else if (err.request) {
        setError("No response received from backend.");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`app ${darkMode ? "dark" : "light"}`}>
      <div className="container">

        <div className="header">
          <div>
            <h1>AI Recruiter System</h1>
            <p className="subtitle">
              Intelligent Candidate Ranking Platform
            </p>
          </div>

          <button
            className="theme-btn"
            onClick={() => setDarkMode(!darkMode)}
          >
            {darkMode ? "☀ Light" : "🌙 Dark"}
          </button>
        </div>

        <div className="input-card">
          <h2>Job Description</h2>

          <textarea
            placeholder="Paste job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />

          <div className="controls">
            <input
              type="number"
              min="1"
              value={topK}
              onChange={(e) => setTopK(e.target.value)}
            />

            <button
              className="rank-btn"
              onClick={rankCandidates}
              disabled={loading}
            >
              {loading ? "Ranking..." : "Rank Candidates"}
            </button>
          </div>
        </div>

        {loading && (
          <div className="loading">
            Ranking candidates...
          </div>
        )}

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {!loading && results.length === 0 && !error && (
          <div className="empty">
            <h2>🤖 AI Recruiter System</h2>
            <p>
              Enter a job description to find the best matching candidates.
            </p>
          </div>
        )}

        <div className="results-grid">
          {results.map((candidate) => (
            <div
              key={candidate.candidate_id}
              className="card"
            >
              <div className="card-top">
                <h3>{candidate.current_title}</h3>

                <span className="score">
                  {candidate.final_score}
                </span>
              </div>

              <p>
                <strong>ID:</strong> {candidate.candidate_id}
              </p>

              <p>
                <strong>Experience:</strong>{" "}
                {candidate.years_experience} years
              </p>

              <p>
                <strong>Location:</strong>{" "}
                {candidate.location}
              </p>

              <div className="skills">
                {candidate.skill_names?.slice(0, 8).map((skill, index) => (
                  <span
                    key={index}
                    className="skill"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}

export default App;