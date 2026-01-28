import React, { useState, useEffect } from "react";

import Questionnaire from "./components/Questionnaire";
import axios from "axios";
import "./App.css";
import QUESTIONS_JSON from "./questions.json";
import Navbar from "./components/Navbar"; 
import ProductCards from "./components/productPage"; // Import the component

function App() {
  const [results, setResults] = useState(() => {
    // Load from localStorage if available
    const saved = localStorage.getItem("results");
    return saved ? JSON.parse(saved) : null;
  });

  const [query, setQuery] = useState("");
  const [laptops, setLaptops] = useState([]);

  // Whenever results change, save to localStorage
  useEffect(() => {
    if (results) {
      localStorage.setItem("results", JSON.stringify(results));
    } else {
      localStorage.removeItem("results");
    }
  }, [results]);

  useEffect(() => {
    // Fetch laptops from backend when results are available
    if (results && !results.processing) {
      axios
        .get("http://127.0.0.1:5000/laptops")
        .then((res) => setLaptops(res.data))
        .catch((err) => console.error(err));
    }
  }, [results]);

  const handleSubmit = async (answers) => {
    setResults({ processing: true });
    const res = await axios.post("http://127.0.0.1:5000/query", { answers });
    setResults(res.data);
    setQuery("");
  };

  const handleUpdateQuery = async () => {
    if (!query) return;
    setResults({ processing: true });
    const res = await axios.post("http://127.0.0.1:5000/query", {
      custom_query: query,
    });
    setResults(res.data);
    setQuery("");
  };

  const handleReset = () => {
    setResults(null);
    localStorage.removeItem("results");
  };

  return (
    <div className="App-container">
      <Navbar />
      {/* <h1>SmartSelect: Tech, Chosen Right</h1> */}
      <div className="App">
        {!results && (
          <Questionnaire questions={QUESTIONS_JSON.questions} onSubmit={handleSubmit} />
        )}
        {results && (
          <div>
            {/* <h3>Modify or add more preferences:</h3> */}
            {/* <div className="query-section">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Type something like 'increase budget' or 'gaming laptop'"
              />
              <button onClick={handleUpdateQuery}>Update Query</button>
              <button className="reset-btn" onClick={handleReset}>Start Over</button>
            </div> */}

            <h2>Recommendations:</h2>
            {/* Show product cards from DB */}
            <ProductCards laptops={laptops} />

            {/* {results.processing ? (
              <div className="loading">Loading recommendations...</div>
            ) : results.items ? (
              results.items.map((item, idx) => (
                <div key={idx} className="recommendation-card">
                  {[
                    "model",
                    "cpu",
                    "ram",
                    "storage",
                    "gpu",
                    "display",
                    "battery",
                    "price_inr",
                    "why",
                  ].map((key) => (
                    <div key={key}>
                      <strong>{key}:</strong> {item[key] || "Unknown"}
                    </div>
                  ))}
                </div>
              ))
            ) : (
              <div>No results found.</div>
            )} */}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;