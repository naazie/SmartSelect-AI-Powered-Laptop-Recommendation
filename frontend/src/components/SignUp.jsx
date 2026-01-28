import React, { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import './login_signup.css'

const API_BASE_URL = "https://mini-project-zhpn.onrender.com";

function Signup({user}) {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setfullName] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Form Submitted!");
    setError('');
    setMessage('');
    setLoading(true);

    if (password !== confirmPassword) {
      setError("Passwords do not match!");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoading(true);

    try {
       console.log("Form Submitted!");
      const response = await axios.post(`${API_BASE_URL}/signup`, {
        username,
        password,
      });

      setMessage(response.data.message || 'Signup successful! Please log in.');
      
      // Redirect to questionnaire page after successful signup
      setTimeout(() => navigate('/questionnaire'), 1500); 

    } catch (err) {
      const msg = err.response?.data?.message || 'Signup failed. Please try a different username.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="body">
      {user ? (
        <>
          <div id="already-signed-in">
            <h2 className='heading-not-signed-in'>{user.username}, you have already signed in</h2>
            <Link className='link-reg' to={'/recommendations'}>
                <button className='not-signed-in-btn'>
                    Go to Recommendations
                </button>
            </Link>
          </div>
      </>
      ) : (
        <>
          <div className="main-cont-reg">
            <h2 className='heading-reg'>Sign Up</h2>
            <form onSubmit={handleSubmit} className="form-reg">
              {error && <p className="auth-error">{error}</p>}
              {message && <p className="auth-success">{message}</p>}

                <div className="form-group">
                  <label htmlFor="username">Username</label>
                  <input
                    type="text"
                    id="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    disabled={loading}
                  />
                  
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={loading}
                  />

                  <label htmlFor="password">Password</label>
                  <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    disabled={loading}
                  />

                  <label htmlFor="confirmPassword">Confirm Password</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    disabled={loading}
                  />
                </div>

              <button type="submit" disabled={loading} className="auth-button">
                {loading ? 'Signing up...' : 'Sign Up'}
              </button>
            </form>
          </div>
        </>
      )}
    </div>
  );
}

export default Signup;