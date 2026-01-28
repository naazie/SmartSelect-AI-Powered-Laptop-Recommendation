// AuthPage.jsx
import React, { useState } from "react";
import Login from "./Login";
import SignUp from "./SignUp";
import "./login_signup.css";

function AuthPage({ user, onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="auth-container">
      <div className={`auth-box ${isLogin ? "" : "right-panel-active"}`}>
        
        {/* LEFT PANEL (Login Form) */}
        <div className="form-container sign-in-container">
          <Login user={user} onAuthSuccess={onAuthSuccess} />
        </div>

        {/* RIGHT PANEL (Signup Form) */}
        <div className="form-container sign-up-container">
          <SignUp user={user} onAuthSuccess={onAuthSuccess} />
        </div>

        {/* OVERLAY (Message Side) */}
        <div className="overlay-container">
          <div className="overlay">
            <div className="overlay-panel overlay-left">
              <h2>Welcome Back!</h2>
              <p>Already have an account? Continue on your Journey.</p>
              <button className="ghost-btn" onClick={() => setIsLogin(true)}>
                Login
              </button>
            </div>
            <div className="overlay-panel overlay-right">
              <h2>Hey, Companion!</h2>
              <p>Don't have an account yet? Sign up and start your Journey.</p>
              <button className="ghost-btn" onClick={() => setIsLogin(false)}>
                Sign Up
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AuthPage;
