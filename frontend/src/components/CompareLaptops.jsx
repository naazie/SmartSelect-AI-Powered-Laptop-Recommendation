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
          <Link to='/recommendations' id='link-part'> 
                <span className='go-back-comp-ka-comp'>
                  <button className="go-back-comp">
                      <i className="fa-solid fa-arrow-left-long"></i>
                      <h4>Go Back</h4>
                  </button>
                </span>
          </Link>
          <div className='heading-comp'>
              <h2 className='recom'>Compare our Recommendations</h2> 
          </div>
          {/* Trying Table */}
          
          <table className="compare-table">
            <thead>
              <tr>
                <th>Features</th>

                {laptops.map((laptop) => (
                  <th key={laptop._id || laptop.model}>
                    {laptop.model || "Unknown Model"}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              <tr>
                <td>Price</td>
                {laptops.map((laptop) => (
                  <td key={laptop._id + "-price"}>Rs {laptop.price_inr}/-</td>
                ))}
              </tr>

              <tr>
                <td>Battery</td>
                {laptops.map((laptop) => (
                  <td key={laptop._id + "-battery"}>{laptop.battery}</td>
                ))}
              </tr>

              <tr>
                <td>Display</td>
                {laptops.map((laptop) => (
                  <td key={laptop._id + "-display"}>{laptop.display}</td>
                ))}
              </tr>

              <tr>
                <td>Storage</td>
                {laptops.map((laptop) => (
                  <td key={laptop._id + "-storage"}>{laptop.storage}</td>
                ))}
              </tr>

              <tr>
                <td>RAM</td>
                {laptops.map((laptop) => (
                  <td key={laptop._id + "-ram"}>{laptop.ram}</td>
                ))}
              </tr>

              <tr>
                <td>CPU</td>
                {laptops.map((laptop) => (
                  <td key={laptop._id + "-cpu"}>{laptop.cpu}</td>
                ))}
              </tr>

              <tr>
                <td>GPU</td>
                {laptops.map((laptop) => (
                  <td key={laptop._id + "-gpu"}>{laptop.gpu}</td>
                ))}
              </tr>
            </tbody>
          </table>
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