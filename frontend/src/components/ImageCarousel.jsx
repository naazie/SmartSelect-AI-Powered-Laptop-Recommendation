import { useState } from "react";
import "./ImageCarousel.css";   // <-- import css

export default function ImageCarousel({ images = [] }) {
    const [current, setCurrent] = useState(0);

  if (!images.length) return null;

  const goTo = (index) => setCurrent(index);

  const next = () => {
    setCurrent((prev) => (prev + 1) % images.length);
  };

  const prev = () => {
    setCurrent((prev) => (prev - 1 + images.length) % images.length);
  };

  return (
    <div className="laptop-carousel">
      <div className="carousel-container">
        <img className="active"
          src={images[current]}
          alt={`Laptop Image ${current + 1}`}
        />
        {/* <div
          className="carousel-track"
          style={{ transform: `translateX(-${current * 100}%)` }}
        >
          {images.map((src, idx) => (
            <img
              key={idx}
              src={src}
              alt="Laptop"
              className="carousel-img active"
            />
          ))}
        </div> */}


        {/* Prev Button */}
        <button className="carousel-btn left" onClick={prev}>
          <i class="fa-solid fa-caret-left"></i>
        </button>

        {/* Next Button */}
        <button className="carousel-btn right" onClick={next}>
          <i class="fa-solid fa-caret-right"></i>
        </button>
      </div>

      {/* Dots */}
      <div className="carousel-dots">
        {images.map((_, index) => (
          <button
            key={index}
            onClick={() => goTo(index)}
            className={`carousel-dot ${index === current ? "active" : ""}`}
          ></button>
        ))}
      </div>
    </div>
  );
}
