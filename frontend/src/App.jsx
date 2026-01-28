import React, { useState, useEffect } from "react";

import Questionnaire from "./components/Questionnaire";
import axios from "axios";
import "./App.css";
import QUESTIONS_JSON from "./questions.json";
import Navbar from "./components/Navbar"; 
import { Route, Routes, useNavigate, Link } from 'react-router-dom';
import ProductInfo from "./components/ProductInfo";
import ProductPage from "./components/productPage";
import CompareLaptops from "./components/CompareLaptops";
import Wishlist from "./components/Wishlist";
import AuthPage from "./components/AuthPage";
import HomePage from "./components/HomePage";


const API_BASE_URL = "https://mini-project-zhpn.onrender.com";


function App() {
  const navigate = useNavigate();

  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [user, setUser] = useState(null); // Optional: Store user info

  const [results, setResults] = useState(() => {
    // Load from localStorage if available
    const saved = localStorage.getItem("results");
    return saved ? JSON.parse(saved) : null;
  });

  const [query, setQuery] = useState("");
  const [laptops, setLaptops] = useState([]);
  const [wishlist, setWishlist] = useState([]);

  const handleWishlistUpdate = async (model, action, query_str) => {
    // 1. Check for token and authentication
    const currentToken = token || localStorage.getItem('token');
    if (!currentToken || !user) {
        console.warn("Cannot update wishlist: User not logged in.");
        // If the component tries to add/remove while the user is logged out, block it.
        return; 
    }

    const method = action === 'add' ? 'post' : 'delete';
    const url = `${API_BASE_URL}/wishlist/${encodeURIComponent(model)}`;
    const data = action === 'add' ? { query_str: query_str } : {}; // Add query_str only for POST (add)

    try {
        const res = await axios({
            method: method,
            url: url,
            data: data,
            headers: {
                Authorization: `Bearer ${currentToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (res.status === 200) {
            console.log(`Wishlist update successful: ${model} ${action}ed.`);
            
            // 2. Update local state based on successful API response
            if (action === 'add') {
                // Find the full laptop object from the main 'laptops' list for local state update
                const laptopToAdd = laptops.find(l => l.model === model);
                if (laptopToAdd && !wishlist.some(l => l.model === model)) {
                    setWishlist(prev => [...prev, laptopToAdd]);
                } else {
                    // Fallback to a full fetch if the laptop object isn't immediately available
                    fetchWishlist();
                }
            } else if (action === 'remove') {
                setWishlist(prev => prev.filter(l => l.model !== model));
            }
        }
    } catch (error) {
        console.error(`Error updating wishlist for ${model}:`, error);

        // 3. Handle 401 Unauthorized error (Expired Token)
        if (error.response && error.response.status === 401) {
            alert("Your session has expired. Please log in again.");
            handleLogout(); // Clears state/storage and redirects
        }
        
        // Handle 400 Bad Request (e.g., missing query_str)
        else if (error.response && error.response.status === 400) {
            alert(`Wishlist failed: ${error.response.data.message || 'Bad Request'}`);
        }
        
        // Ensure local state is cleared if the API failed to prevent desync
        fetchWishlist(); 
    }
};

  // Whenever results change, save to localStorage
  useEffect(() => {
    if (results) {
      localStorage.setItem("results", JSON.stringify(results));
    } else {
      localStorage.removeItem("results");
    }
  }, [results]);

  useEffect(() => {
    const currentToken = token || localStorage.getItem("token");

    // Function to fetch the latest 5 laptops (either from the recent search or personalized history)
    const fetchLaptops = async () => {
        try {
            // Include Authorization header only if a token exists
            const headers = currentToken ? { Authorization: `Bearer ${currentToken}` } : {};
            
            const res = await axios.get(`${API_BASE_URL}/laptops`, { headers });
            
            // The response will be the latest 5 search results (personalized if logged in)
            setLaptops(res.data);
        } catch (err) {
            console.error("Error fetching laptops:", err);
            setLaptops([]); // Clear on error
        }
    };

    // 1. If a search just completed (results != null and not processing), fetch the new data.
    if (results && !results.processing) {
        fetchLaptops();
    } 
    // 2. If the authentication state changes (token), or on initial load, 
    // fetch the user's personalized history (if they are logged in).
    else if (token !== undefined) {
        fetchLaptops();
    }

  }, [results, token]); // Dependency on 'token' is now CRITICAL.

   // In App.js, replace the existing fetchWishlist function with this:
  const fetchWishlist = async () => {
    const currentToken = localStorage.getItem('token');
    // Only proceed if the user is authenticated
    if (!currentToken || !user) {
        setWishlist([]);
        return;
    }

    try {
        console.log("Fetching wishlist for user:", user.username);
        const res = await axios.get(`${API_BASE_URL}/wishlist`, {
            headers: {
                Authorization: `Bearer ${currentToken}`,
            },
        });

        // 🛑 FIX: Ensure res.data is an array before setting state
        if (Array.isArray(res.data)) {
            setWishlist(res.data);
        } else {
            // Handle unexpected non-array format gracefully
            console.warn("Wishlist response was not an array. Clearing wishlist state.");
            setWishlist([]);
        }
    } catch (error) {
        console.error("Error fetching wishlist:", error);
        // If fetching fails (e.g., 401), clear the list
        setWishlist([]); 
    }
  };
  
  useEffect(() => {
    fetchWishlist();
  // DEPENDENCY FIX: Now runs whenever 'user' changes (login/logout)
  }, [user]); 

  // 2. NEW: Function to decode token (simplistic) and set user info
  const decodeToken = (jwtToken) => {
    try {
      // Note: This is a basic client-side decode. 
      // It doesn't verify the signature, only reads the payload.
      const payload = JSON.parse(atob(jwtToken.split('.')[1]));
      setUser({ username: payload.username, id: payload.user_id });
    } catch (e) {
      console.error("Failed to decode token:", e);
      setUser(null);
      setToken(null);
      localStorage.removeItem("token");
    }
  };

  // 3. NEW: Effect to initialize user from token
  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
      decodeToken(token);
    } else {
      localStorage.removeItem("token");
      setUser(null);
    }
  }, [token]);

  // 4. NEW: Handle Logout
  const handleLogout = () => {
    setToken(null);
    navigate('/');
  };

  // 5. NEW: Handle successful Login/Signup
  const handleAuthSuccess = (token) => {
    setToken(token);
    navigate('/questionnaire'); // Redirect after successful auth
  };

  // const handleSubmit = async (answers) => {
  //   setResults({ processing: true });
  //   navigate('/recommendations');
  //   const res = await axios.post("http://127.0.0.1:5000/query", { answers });
  //   setResults(res.data);
  //   setQuery("");
  // };

  // ... existing code

  const handleSubmit = async (answers) => {
  setResults({ processing: true });
  navigate('/recommendations');
  const currentToken = localStorage.getItem('token');
  
  // Determine the data payload (no need to include user_id in the payload)
  const dataToSend = { answers }; 

  try {
    const res = await axios.post(
        "http://127.0.0.1:5000/query",
        dataToSend, 
        {
           headers: currentToken ? { Authorization: `Bearer ${currentToken}` } : {},
        }
    );

    setResults(res.data);

    // CRITICAL FIX: Set the 'query' state based on the response.
    const generatedQuery = res.data.keyword || res.data.query_str || "Questionnaire Results";
    setQuery(generatedQuery);

  } catch (error) {
    console.error("Error submitting questionnaire:", error);
    setResults(null); // Clear processing state on error
  }
};


  // const handleUpdateQuery = async () => {
  //   if (!query) return;
  //   setResults({ processing: true });
  //   // The backend should handle combining the original answers with the custom_query
  //   const res = await axios.post("http://127.0.0.1:5000/query", {
  //     custom_query: query,
  //   });
  //   setResults(res.data);
  //   setQuery("");
  // };

const handleUpdateQuery = async () => {
  if (!query) return;
  setResults({ processing: true });
  const currentToken = localStorage.getItem('token');

  // Determine the data payload (no need to include user_id in the payload)
  const dataToSend = { custom_query: query };
  
  const res = await axios.post(
    "http://127.0.0.1:5000/query",
    dataToSend, 
    {
       headers: currentToken ? { Authorization: `Bearer ${currentToken}` } : {},
    }
  );

  setResults(res.data);
};


  const handleReset = () => {
    setResults(null);
    localStorage.removeItem("results");
  };

  return (
    <div className="App-container">
      <Navbar user={user} onLogOut={handleLogout} />
      <div className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />

          <Route path="/auth" element={<AuthPage user={user} onAuthSuccess={handleAuthSuccess} />} />
          
          <Route path="/questionnaire" element={
            <Questionnaire user={user} questions={QUESTIONS_JSON.questions} onSubmit={handleSubmit} />
          } />

          <Route path="/recommendations" element={
          <>
            {results ? ( 
              results.processing ? (
                <div className="loading">
                  <div className="loader"></div>
                </div>
              ) : (
                  <ProductPage user={user} 
                      laptops={laptops}
                      query={query}
                      setQuery={setQuery}
                      onUpdateQuery={handleUpdateQuery}
                      onReset={handleReset}
                      wishlist={wishlist}
                      onWishlistUpdate={handleWishlistUpdate}
                  />
              )
            ) : (
              <div id="not-signed-in">
                <h2 id='heading-not-signed-in'>Just a secccc.... <br />You haven't logged in yet
                </h2>
              
                <Link id='not-signed-in-link' to={'/auth'}>
                    <button className='not-signed-in-btn'>
                        Log In
                    </button>
                </Link>
              </div>
            )}
          </>
        } />
        <Route path="/products/:id" element={
          <ProductInfo user={user} laptops={laptops} />
        } />

        <Route path="/compareLaptops" element={
          <CompareLaptops user={user} laptops={laptops}/>
        }/>

        <Route path="/wishlist" element={
          <Wishlist user={user} wishlist = {wishlist} onWishlistUpdate={handleWishlistUpdate}/>
        }/>

        </Routes>  
      </div>
    </div>
  );
}

export default App;
