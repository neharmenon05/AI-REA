import React, { useEffect, useState } from "react";
import "../styles/buy-property.css";


const API_URL = "http://127.0.0.1:8000"; // backend URL

export default function BuyerPage() {
  const [properties, setProperties] = useState([]);
  const [filteredProps, setFilteredProps] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [cities, setCities] = useState([]);
  const [localities, setLocalities] = useState([]);
  const [selectedCity, setSelectedCity] = useState("");
  const [selectedLocality, setSelectedLocality] = useState("");
  const [priceRange, setPriceRange] = useState({ min: "", max: "" });

  useEffect(() => {
    const fetchProperties = async () => {
      try {
        const res = await fetch(`${API_URL}/api/marketplace/properties`);
        const data = await res.json();
        setProperties(data);
        setFilteredProps(data);

        // extract unique cities
        const uniqueCities = [...new Set(data.map((p) => p.location))];
        setCities(uniqueCities);
      } catch (err) {
        console.error("Failed to load properties:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, []);

  // Update localities when city changes
  useEffect(() => {
    if (selectedCity) {
      const filteredLocalities = [
        ...new Set(
          properties
            .filter((p) => p.location === selectedCity)
            .map((p) => p.sublocality)
        ),
      ];
      setLocalities(filteredLocalities);
      setSelectedLocality(""); // reset locality
    } else {
      setLocalities([]);
      setSelectedLocality("");
    }
  }, [selectedCity, properties]);

  // Apply filters
  const applyFilters = () => {
    let temp = [...properties];
    if (selectedCity) temp = temp.filter((p) => p.location === selectedCity);
    if (selectedLocality)
      temp = temp.filter((p) => p.sublocality === selectedLocality);
    if (priceRange.min) temp = temp.filter((p) => Number(p.price) >= Number(priceRange.min));
    if (priceRange.max) temp = temp.filter((p) => Number(p.price) <= Number(priceRange.max));
    setFilteredProps(temp);
  };

  if (loading) return <p style={{ textAlign: "center" }}>Loading properties...</p>;

  return (
    <div className="buyer-container">
      <h1>Available Properties</h1>

      {/* Filters */}
      <div className="filters">
        <select value={selectedCity} onChange={(e) => setSelectedCity(e.target.value)}>
          <option value="">Select City</option>
          {cities.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <select
          value={selectedLocality}
          onChange={(e) => setSelectedLocality(e.target.value)}
          disabled={!localities.length}
        >
          <option value="">Select Locality</option>
          {localities.map((l) => (
            <option key={l} value={l}>{l}</option>
          ))}
        </select>

        <input
          type="number"
          placeholder="Min Price"
          value={priceRange.min}
          onChange={(e) => setPriceRange({ ...priceRange, min: e.target.value })}
        />
        <input
          type="number"
          placeholder="Max Price"
          value={priceRange.max}
          onChange={(e) => setPriceRange({ ...priceRange, max: e.target.value })}
        />

        <button className="btn apply-btn" onClick={applyFilters}>Apply Filters</button>
      </div>

      {/* Properties */}
      <div className="properties-grid">
        {filteredProps.length === 0 ? (
          <p style={{ textAlign: "center" }}>No properties match the filters.</p>
        ) : (
          filteredProps.map((p) => (
            <div key={p.id} className="property-card">
              <div className="property-images">
                {p.images && p.images.length > 0 ? (
                  <img src={p.images[0]} alt={p.title} />
                ) : (
                  <div className="no-image">No Image</div>
                )}
              </div>
              <div className="property-details">
                <h2>{p.title}</h2>
                <p>
                  <strong>Location:</strong> {p.sublocality}, {p.location}
                </p>
                <p>
                  <strong>Type:</strong> {p.property_type}, <strong>BHK:</strong> {p.bhk}
                </p>
                <p>
                  <strong>Size:</strong> {p.size} sqft | <strong>Price:</strong> ₹{p.price}
                </p>
                {p.description && <p>{p.description}</p>}
                <p>
                  <strong>Owner:</strong> {p.owner_name} | <strong>Contact:</strong> {p.owner_phone}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
