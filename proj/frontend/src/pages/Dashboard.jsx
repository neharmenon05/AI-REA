import MainLayout from "../layouts/MainLayout";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const submitQuery = async (e) => {
    e.preventDefault();
    navigate("/results", { state: { query } });
  };

  return (
    <MainLayout>
      <div className="dashboard-container">
        <h2 className="dashboard-title">
          Property Analysis Dashboard
        </h2>

        {/* QUERY INPUT */}
        <form className="query-box" onSubmit={submitQuery}>
          <div className="query-box-header">
            <h3 className="query-box-title">
              Describe the property you want to analyze
            </h3>
            <p className="query-box-description">
              Kindly mention the number of rooms, area, and square feet of property
            </p>
          </div>

          <input
            type="text"
            className="query-input"
            placeholder="Example: 3 BHK apartment in Kharadi Pune, 1500 sqft for investment"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
          />

          <button type="submit" className="btn-analyze">
            Analyze Property
          </button>
        </form>
      </div>
    </MainLayout>
  );
}