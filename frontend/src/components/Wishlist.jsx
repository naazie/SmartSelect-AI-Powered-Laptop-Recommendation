import React from 'react'
import ProductCard from './productCard'
import { Link } from 'react-router-dom';
import "./wishlist.css";

function Wishlist({ user, wishlist, onWishlistUpdate}) {
  return (
    <>
        {user ? (
            wishlist.length == 0 ? (
                <div id="not-signed-in">
                <h2 id='heading-not-signed-in'>No Items In The Wishlist <br /> It Looks Like You Haven't Found What You're Looking For Yet :(
                </h2>
                
                <Link id='not-signed-in-link' to={'/recommendations'}>
                    <button className='not-signed-in-btn'>
                        Go to Recommendations
                    </button>
                </Link>
            </div>
            ):(
                <div className='main-cont-wish'>
                    <div className="pr" id = "prod">
                        {wishlist.map((item, idx) => (
                        <ProductCard 
                            user={user} 
                            key={item._id || item.model || idx} 
                            item={item}
                            initialWishlist={true} 
                            onWishlistUpdate={onWishlistUpdate}/>
                        ))}
                    </div>
                    <div class="go-to-rec">
                        <Link to="/recommendations"> 
                        <button>
                            Go to Recommendations
                        </button>
                        </Link>
                    </div>
                </div>
            )
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

export default Wishlist