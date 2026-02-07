import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/marketplace.css";
import { FaSearch, FaHome, FaTag } from "react-icons/fa";

const Marketplace = () => {
  const navigate = useNavigate();

  return (
    <div className="marketplace-container">
      <div className="marketplace-card">
        <h1>Property Marketplace</h1>
        <p>Buy, sell, or explore properties easily</p>

        <div className="marketplace-actions">
          <div
            className="action-card"
            onClick={() => navigate("/marketplace/buy")}
          >
            <FaSearch className="action-icon" />
            <span>Find Property</span>
          </div>

          <div
            className="action-card"
            onClick={() => navigate("/marketplace/sell")}
          >
            <FaTag className="action-icon" />
            <span>List Property</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Marketplace;
