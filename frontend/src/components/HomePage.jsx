import React from "react";
import { useNavigate } from "react-router-dom";
import "./HomePage.css";

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="home-page">
        <h1>
            Welcome to Smart Select: Tech Chosen Right
        </h1>
        <h2>
            <b>Your journey to finding the perfect laptop starts here.</b>
        </h2>
        <h3>
            About SmartSelect
        </h3>
        <p>
            In today’s fast-changing world of technology, choosing the right gadget can be confusing, especially for people who are not able to keep up with the latest trends or technical terms. With hundreds of models, complicated specifications, and paid reviews, it’s easy to feel lost or make a purchase that doesn’t truly meet your needs.
        </p>
        <p>
            SmartSelect is built to solve this problem. It helps you find the perfect laptop or smartphone that fits your budget, lifestyle, and purpose, without the stress of endless research. By combining intelligent data analysis and real user feedback, SmartSelect gives you honest, easy-to-understand, and reliable product suggestions you can trust.
        </p>
        <p>
            Whether you’re a student buying your first laptop, a professional looking for performance, or just someone who wants a reliable phone, SmartSelect makes sure your choice is smart, simple, and right for you.
        </p>
        <h3>
            What we offer?
        </h3>
        <h4>
            Smart Recommendations
        </h4>
        <p>
            Instead of browsing endless websites or watching confusing reviews, SmartSelect gives you a curated shortlist of the best products that match your needs. You simply tell us your preferences, like your budget, usage (for work, gaming, or study), and what matters most to you, and the system filters through data to present only the most relevant options. This saves you time, effort, and guesswork while ensuring every suggestion fits your actual requirements.
        </p>
        <h4>
            Real Review Insights
        </h4>
        <p>
            Every recommendation is supported by insights drawn from thousands of genuine customer reviews. SmartSelect doesn’t just rely on star ratings, it studies what real users are saying about key features like battery life, screen quality, camera performance, and durability. This helps you understand the true strengths and weaknesses of each product before making a decision, based on real experiences rather than marketing claims.
        </p>
        <h4>
            Transparent Comparisons
        </h4>
        <p>
            Once you have your shortlist, SmartSelect presents everything in a clear, simple interface. You can easily compare specifications, see the pros and cons side by side, and get a summarized view of real-world performance. No technical jargon, no complicated tables — just straightforward, trustworthy information to help you make a confident choice.
        </p>
        <h3>
            Who It’s For?
        </h3>
        <p>
            Students: For students, choosing the right laptop often means balancing performance with affordability. SmartSelect identifies laptops optimized for academic work, project requirements, and long-term reliability, ensuring every student invests in a device that supports both learning and leisure.<br/>
            Working Professionals: Professionals often lack the time to research dozens of devices. SmartSelect helps them make quick, data-backed decisions by summarizing performance, user reviews, and value propositions in one place. It’s like having a personal tech consultant that works instantly.<br/>
            Everyday Users: For non-technical individuals, from parents buying their first smartphone to older adults upgrading their devices, SmartSelect translates complex specifications into simple, understandable insights. It removes the fear of making an expensive mistake and builds confidence through clarity.
        </p>
        <h3>
            In Essence
        </h3>
        <p>
            SmartSelect isn’t just about finding your next gadget, it’s about helping you make smarter, more confident tech choices.<br/>
            It saves your time, makes comparisons simple, and gives clear, trustworthy recommendations so you can choose what truly fits your needs.<br/>
            By combining intelligent technology with real user insights, SmartSelect transforms the way people buy gadgets, with transparency, trust, and simplicity at its core.
        </p>
        <button onClick={() => navigate("/auth")}>
            Get Started
        </button>
    </div>
  );
};

export default HomePage;