import React from 'react';
import { useParams } from 'react-router-dom';
import { Link } from 'react-router-dom';
import "./ProductInfo.css"
import ImageCarousel from "./ImageCarousel.jsx"
import ReviewSection from './ReviewSection.jsx';

// import './ProductInfo.css';

// Define the keys that might be considered "More Info" (excluding the ones already shown in the card body if desired)
const DETAIL_KEYS = [
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
    "form_input",
    "Why_in",
    "what_it_says"
];

function ProductInfo({ user, laptops }) {

  const { id } = useParams();

  // / 🚨 CRITICAL FIX: Ensure both sides are strings for comparison.
  // We assume the ObjectId object is stored under the key '_id'.
  const item = laptops.find(laptop => {
      // 1. Check if the _id field exists.
      if (laptop._id) {
          // 2. Convert the ObjectId object to its string representation 
          //    (e.g., using .toString() or .toHexString()) and compare it to the URL ID.
          //    We use String() for maximum safety.
          return String(laptop._id) === id;
      }
      return false;
  });

  if (!item) {
    return (
        <div className="product-info-details">
            <h2>Error: Product details not found for ID: {id}</h2>
        </div>
    );
  }

  return (
    <>
      {user ? (
        <div className="cont-info">
          <div className="product-info-main-cont">
            <div className="general-info">
              <div className="prod-img">
                <ImageCarousel images={item.images}/>
              </div>
              <div className="prod-gen-deets">
                <h2>{item.model} <br /> {item.price_inr} </h2> 
                <hr />
                <p>{item.Why_in}</p>
              </div>
            </div>

            <div className="prod-specs">
              
              <div className="tech-specs">
                <h2>Specifications</h2>
                <div className="jargon-wala-specs">
                  <div className="model-specs">
                    <h3>What the model offers</h3>
                    <div className="specs-wrapper">
                      <div className="specs">
                        <table className="prod-spec-table">
                          <tbody>
                            <tr>
                              <td><strong>Model</strong></td>
                              <td>{item.model}</td>
                            </tr>
                            <tr>
                              <td><strong>CPU</strong></td>
                              <td>{item.cpu}</td>
                            </tr>
                            <tr>
                              <td><strong>RAM</strong></td>
                              <td>{item.ram}</td>
                            </tr>
                            <tr>
                              <td><strong>Storage</strong></td>
                              <td>{item.storage}</td>
                            </tr>
                            <tr>
                              <td><strong>GPU</strong></td>
                              <td>{item.gpu}</td>
                            </tr>
                            <tr>
                              <td><strong>Display</strong></td>
                              <td>{item.display}</td>
                            </tr>
                            <tr>
                              <td><strong>Battery</strong></td>
                              <td>{item.battery}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  <div className="your-specs">
                    <h3>What you need</h3>
                    <div className="specs-wrapper">
                      <div className="specs">
                        {/* <div>
                          <strong>Need to add from db, this is dummy</strong>
                        </div> */}
                        <table className="prod-spec-table">
                          <tbody>
                            {Object.entries(item.form_input || {}).map(([key, value]) => (
                              <tr key={key}>
                                <td><strong>{key.charAt(0).toUpperCase() + key.slice(1)}</strong></td>
                                <td>{value}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="wo_jargon_specs"></div>
                  <h3>What it means</h3>
                  <div className="specs">
                    <table className="prod-spec-table">
                      <tbody>
                        {Object.entries(item.what_it_says || {}).map(([key, value]) => (
                          <tr key={key}>
                            <td><strong>{key.charAt(0).toUpperCase() + key.slice(1)}</strong></td>
                            <td>{value}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
              </div>
            </div>

            <ReviewSection model={item.model} />

          </div>
          {/* <div className="prod-specs">
          </div> */}

          
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
  );
}

export default ProductInfo;
