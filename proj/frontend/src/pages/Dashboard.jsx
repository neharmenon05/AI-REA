import MainLayout from "../layouts/MainLayout";
import { useState, useEffect, useRef } from "react";  
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [query, setQuery] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const navigate = useNavigate();
  const recognitionRef = useRef(null);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setQuery(transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    } else {
      setIsSupported(false);
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  // Listen for assistant auto-fill events
  useEffect(() => {
    const handler = (e) => {
      setQuery(e.detail.query);
    };
    window.addEventListener("assistant-fill-query", handler);
    return () => window.removeEventListener("assistant-fill-query", handler);
  }, []);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const submitQuery = async (e) => {
    e.preventDefault();
    navigate("/results", { state: { query } });
  };

  return (
    <MainLayout>
      <div className="dashboard-container">
        <h2 className="dashboard-title">
          Property Analysis Dashboard
        </h2>

        {/* QUERY INPUT */}
        <form className="query-box" onSubmit={submitQuery}>
          <div className="query-box-header">
            <h3 className="query-box-title">
              Describe the property you want to analyze 
            </h3>
            <p className="query-box-description">
              Kindly mention the number of rooms, area, and square feet of property
            </p>
          </div>

          <div className="input-wrapper">
            <input
              type="text"
              className="query-input"
              placeholder="Example: 3 BHK apartment in Kharadi Pune, 1500 sqft for investment"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
            />
            
            {isSupported && (
              <button
                type="button"
                onClick={toggleVoiceInput}
                className={`voice-btn ${isListening ? 'listening' : ''}`}
                title={isListening ? "Stop listening" : "Start voice input"}
              >
                {isListening ? (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" y1="19" x2="12" y2="22"/>
                    <circle cx="12" cy="12" r="3" fill="currentColor"/>
                  </svg>
                ) : (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" y1="19" x2="12" y2="22"/>
                  </svg>
                )}
              </button>
            )}
          </div>

          {isListening && (
            <p className="listening-indicator">
              🎤 Listening... Speak now
            </p>
          )}

          <button type="submit" className="btn-analyze">
            Analyze Property
          </button>
        </form>
      </div>
    </MainLayout>
  );
}