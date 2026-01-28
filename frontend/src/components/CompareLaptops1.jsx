import React, { useEffect, useRef } from 'react'; // 👈 Reworked this line for clarity and robustness
import { useParams, Link } from 'react-router-dom';
import "./CompareLaptops.css";

// Define the keys we want to display and format them (keeping this as-is)
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
];

function CompareLaptops({ user, laptops }) {
  // 1. Declare the ref inside the function component
  const targetDivRef = useRef(null);
  
  // 2. Define the scroll logic inside useEffect to run once on mount
  useEffect(() => {
    if (targetDivRef.current) {
      targetDivRef.current.scrollIntoView({
        behavior: 'smooth', 
        block: 'center',    
        inline: 'nearest'   
      });
    }
  }, []); 

  return (
    <>
      {user ? (
        // 3. Attach the ref to the div you want to center
        // Note: It's better practice to use 'className' instead of 'class' in JSX/React
        <div ref={targetDivRef} className='main-cont-coompare'>
          <div className='heading-comp'>
              <Link to='/recommendations' id='link-part'> 
                <span className='go-back-comp-ka-comp'>
                  <button className="go-back-comp">
                      <i className="fa-solid fa-arrow-left-long"></i>
                      <h4>Back to Laptops</h4>
                  </button>
                </span>
              </Link>
              <h2 className='recom'>Compare our Recommendations</h2> 
          </div>
          

          <div className='actual-comp-table'>
            <div className="titles-comp">
              <div className="inner-cont-comp-left">
                <h3>Features</h3>
              </div>
              {laptops.map((laptop, index) => {
                  // Determine if this is the last column to apply inner-cont-comp-right
                  const isLast = index === laptops.length - 1;
                  const className = isLast ? "inner-cont-comp-right" : "inner-cont-comp";
                  
                  return (
                      <div key={laptop._id || laptop.model} className={className}>
                          <h3>{laptop.model || "Unknown Model"}</h3>
                      </div>
                  );
              })}
            </div>
            <div className="cont-comp">
              <div className="inner-cont-comp-left">
                  <p className='features-comp'>Price</p>
                  <p className='features-comp'>Battery</p>
                  <p className='features-comp'>Display</p>
                  <p className='features-comp'>Storage</p>
                  <p className='features-comp'>RAM</p>
                  <p className='features-comp'>CPU</p>
                  <p className='features-comp'>GPU</p>
              </div>
              {laptops.map((laptop, index) => {
                const isLast = index === laptops.length - 1;
                const className = isLast? "inner-cont-comp-right" : "inner-cont-comp";
                return (
                  <div key={laptop._id + "-data"} className={className}> 
                    <div className="features-comp">
                      <p>Rs {laptop.price_inr}/-</p>
                    </div>
                    <div className="features-comp">
                      <p>{laptop.battery}</p>
                    </div>
                    <div className="features-comp">
                      <p>{laptop.display}</p>
                    </div>
                    <div className="features-comp">
                      <p>{laptop.storage}</p>
                    </div>
                    <div className="features-comp">
                      <p>{laptop.ram}</p>
                    </div>
                    <div className="features-comp">
                      <p>{laptop.cpu}</p>
                    </div>
                    <div className="features-comp">
                      <p>{laptop.gpu}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
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

export default CompareLaptops;