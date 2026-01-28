import React, { useRef, useEffect } from 'react';
import './productPage.css';
import ProductCard from './productCard';
import { Link } from 'react-router-dom';

function ProductCards({
  user,
  laptops,
  query,
  setQuery,
  onUpdateQuery,
  onReset,
  wishlist,
  onWishlistUpdate
}) {

  const targetDivRef = useRef(null);

  // Auto-scroll once component mounts
  useEffect(() => {
    if (targetDivRef.current) {
      targetDivRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'nearest'
      });
    }
  }, []);

  // 🚨 WAIT UNTIL LAPTOPS IS READY → show loader instead of breaking
  if (!Array.isArray(laptops)) {
    return (
      <div className="loading">
        <div className="loader"></div>
      </div>
    );
  }

  // 🟡 If laptops loaded but empty → show refine box
  if (laptops.length === 0) {
    return (
      <div id="not-signed-in">
        <h2 id='heading-not-signed-in'>
          Oh Noo... <br />No laptops found on your criteria
        </h2>

        <Link id='not-signed-in-link' to={'/questionnaire'}>
          <button className='not-signed-in-btn'>Back to Quiz</button>
        </Link>
      </div>
    );
  }

  // 🔴 If user not logged in
  if (!user) {
    return (
      <div id="not-signed-in">
        <h2 id='heading-not-signed-in'>
          Just a secccc.... <br />You haven't logged in yet
        </h2>

        <Link id='not-signed-in-link' to={'/auth'}>
          <button className='not-signed-in-btn'>Log In</button>
        </Link>
      </div>
    );
  }

  // 🟢 Main UI — only runs when laptops is READY & user is LOGGED IN
  return (
    <div className='product-cards-container'>

      {/* Top search/refine bar */}
      <div id="topbar" className="query-section">
        <input id='topbar-ip'
          type="text"
          placeholder="Refine your query..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        <button id='search' onClick={onUpdateQuery}>
          <i className="fa-solid fa-magnifying-glass"></i>
        </button>
      </div>

      {console.log("LAPTOPS = ", laptops)}

      <div className="main-cont" ref={targetDivRef}>

        <div id="prod">
          {laptops.map((item, idx) => (
            <ProductCard
              user={user}
              key={item._id || idx}
              item={item}
              initialWishlist={wishlist.some(w => w.model === item.model)}
              onWishlistUpdate={onWishlistUpdate}
            />
          ))}
        </div>

        <div id="go-to-compare">
          <Link to="/compareLaptops">
            <button>Compare</button>
          </Link>
        </div>

      </div>
    </div>
  );
}

export default ProductCards;
