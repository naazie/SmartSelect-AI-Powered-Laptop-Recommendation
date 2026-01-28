import React, { useState, useEffect } from 'react'
import './productCard.css'
import { Link } from 'react-router-dom';
import axios from 'axios';

// Define the keys we want to display and format them
const DISPLAY_KEYS = [
    "_id",
    "model",
    "cpu",
    "ram",
    "storage",
    "gpu",
    "display",
    "battery",
    "price_inr",
    "why",
    "images",
];

const API_BASE_URL = "https://mini-project-zhpn.onrender.com";

function ProductCard({initialWishlist, user, item, onWishlistUpdate }) {
  const [isWishlisted, setIsWishlisted] = useState(initialWishlist || false)

  useEffect(() => {
    setIsWishlisted(initialWishlist || false);
  }, [initialWishlist]);

  const handleWishlistToggle = async () => {
    if(!user) {
      alert("Please log in before you can add items to your wishlist")
      return;
    }

    const action = isWishlisted ? "remove" : "add";
    // 🛑 FIX 1: Retrieve the query_str associated with this specific recommendation.
    // This is passed to the backend when adding a new item.
    // Use optional chaining for safety.
    const queryStrForAdd = item.form_input?.query_str || "Custom Search"; 

    // 🛑 FIX 2: Replace the direct axios call with the prop function from App.js
    try {
        // The onWishlistUpdate function handles the API call, headers, and token.
        // It requires: (model, action, query_str)
        
        await onWishlistUpdate(
            item.model, 
            action, 
            // Only pass queryStrForAdd if we are adding the item
            action === 'add' ? queryStrForAdd : null
        );

        // If the update was successful (handled inside App.js's prop function)
        // We only toggle the state if the prop function succeeds.
        setIsWishlisted(prev => !prev);
        
    }
    catch(error) {
      // The error handling is now largely done in App.js, but we log here too
      console.error("Wishlist operation failed:", error);
      // Optional: alert("Failed to update wishlist. Please try again.");
    }
  }


  const productId = item._id ? item._id.toString() : item.id; // Use item.id as fallback
  return (
    <>
      {user ? (
        <div className="recommendation-card">
          <div id="prod-img">
            <img
              src={item.images?.[0]}
              alt={item.model}
              style={{ width: "100%", borderRadius: "8px" }}
            />
          </div>
          <div id="prod-deets">
            <div className="prod-model-comp">
              <h3 className="product-model">{item.model || "Unknown Model"} <br /> ₨ {item.price_inr}/-
              </h3>
            </div>
            {/* <h4 className='prod-price'>₨ {item.price_inr}/-</h4> */}
            <div className="prod-why-comp">
              <p id="prod-why">{item.why}</p>
            </div>
          </div>

          <div className="more-info">
            <Link id='more-info-link' to={`/products/${productId}`}> 
              <button id='info'>
                More Info
              </button>
            </Link>
            <button id='wish' onClick={handleWishlistToggle}>
              <i id='heart' class={`fa-solid fa-heart ${isWishlisted ? 'wishlisted': 'not wishlisted'}`} style={{color: isWishlisted ? '#D25D5D' : '#b9b7b7'}}></i>
            </button>
          </div>
            {/* {DISPLAY_KEYS.map((key) => (
                <div key={key}>
                    <strong>{key.replace('_inr', '').toUpperCase()}:</strong> {item[key] || "Unknown"}
            
              
                    </div>
            ))} */}
        </div>
      ):(
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
  )
}

export default ProductCard
