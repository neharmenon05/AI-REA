import React, { useState, useEffect } from "react";  
import "../styles/sell-property.css";
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";


export default function SellProperty() {
  const [step, setStep] = useState(1);
  const [images, setImages] = useState([]);
  const [form, setForm] = useState({
    title: "",
    location: "",
    sublocality: "",
    property_type: "Apartment",
    bhk: "2 BHK",
    size: "",
    floor: "",
    total_floors: "",
    property_age: "",
    price: "",
    furnishing: "",
    parking: 0,
    description: "",
    owner_name: "",
    owner_phone: "",
    owner_email: "",
    amenities: {},
  });

  const steps = ["Basic Info", "Features", "Description", "Photos", "Contact"];

    useEffect(() => {
    const handler = (e) => {
      const fields = e.detail;
      setForm(prev => ({
        ...prev,
        ...fields,
      }));
      
      // If description was filled, jump to that step
      if (fields.description && step < 3) {
        setStep(3);
      }
    };
    
    window.addEventListener("assistant-fill-sell-form", handler);
    return () => window.removeEventListener("assistant-fill-sell-form", handler);
  }, [step]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setForm((p) => ({ ...p, [name]: type === "number" ? Number(value) : value }));
  };

  const handleFileChange = (e) => {
    const files = [...e.target.files].slice(0, 6);
    setImages(files);
  };

  const next = () => setStep((s) => Math.min(s + 1, steps.length));
  const prev = () => setStep((s) => Math.max(s - 1, 1));

  const handleSubmit = async () => {
    if (!form.title || !form.location || !form.sublocality || !form.size || !form.price ||
        !form.owner_name || !form.owner_phone || !form.owner_email) {
      alert("Please fill all required fields");
      return;
    }

    const formData = new FormData();
    Object.keys(form).forEach((k) => {
      if (k !== "amenities") formData.append(k, form[k]);
    });
    formData.append("amenities", JSON.stringify(form.amenities));
    images.forEach((img) => formData.append("images", img));

    try {
      const res = await fetch(`${API_URL}/api/marketplace/submit`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        alert("Property submitted successfully!");
        window.location.reload();
      } else {
        alert("Error: " + data.detail);
      }
    } catch (err) {
      alert("Submission failed: " + err.message);
    }
  };

  return (
    <div className="sell-container">
      <h1>List Your Property</h1>
      <div className="progress">
        {steps.map((s, i) => (
          <div key={i} className={`step ${step >= i + 1 ? "active" : ""}`}>{s}</div>
        ))}
      </div>

      {step === 1 && (
        <div className="card glass">
          <h2>Basic Info</h2>
          <label>Title *</label>
          <input name="title" value={form.title} onChange={handleChange} placeholder="Enter property title" />

          <label>City *</label>
          <input name="location" value={form.location} onChange={handleChange} placeholder="City" />

          <label>Locality *</label>
          <input name="sublocality" value={form.sublocality} onChange={handleChange} placeholder="Locality / Neighborhood" />

          <label>Property Type</label>
          <select name="property_type" value={form.property_type} onChange={handleChange}>
            <option>Apartment</option>
            <option>House</option>
            <option>Villa</option>
            <option>Other</option>
          </select>

          <label>BHK</label>
          <select name="bhk" value={form.bhk} onChange={handleChange}>
            <option>1 BHK</option>
            <option>2 BHK</option>
            <option>3 BHK</option>
            <option>4+ BHK</option>
            <option>Other</option>
          </select>

          <label>Size (sqft) *</label>
          <input name="size" type="number" value={form.size} onChange={handleChange} placeholder="Area in sqft" />
        </div>
      )}

      {step === 2 && (
        <div className="card glass">
          <h2>Features</h2>
          <label>Floor</label>
          <input name="floor" type="number" value={form.floor} onChange={handleChange} placeholder="Floor number" />

          <label>Total Floors</label>
          <input name="total_floors" type="number" value={form.total_floors} onChange={handleChange} placeholder="Total floors in building" />

          <label>Property Age</label>
          <input name="property_age" type="number" value={form.property_age} onChange={handleChange} placeholder="Years old" />

          <label>Price *</label>
          <input name="price" type="number" value={form.price} onChange={handleChange} placeholder="Price" />

          <label>Furnishing Status</label>
          <select name="furnishing" value={form.furnishing} onChange={handleChange}>
            <option value="">Select</option>
            <option>Fully Furnished</option>
            <option>Semi Furnished</option>
            <option>Unfurnished</option>
            <option>Other</option>
          </select>

          <label>Parking Spaces</label>
          <input name="parking" type="number" value={form.parking} onChange={handleChange} placeholder="Number of parking spaces" />
        </div>
      )}

      {step === 3 && (
        <div className="card glass">
          <h2>Description</h2>
          <label>Property Description</label>
          <textarea value={form.description} onChange={(e) => setForm({...form, description: e.target.value})} placeholder="Write details about your property"></textarea>
        </div>
      )}

      {step === 4 && (
        <div className="card glass">
          <h2>Photos</h2>
          <input type="file" multiple accept="image/*" onChange={handleFileChange} />
          {images.length > 0 && (
            <div className="preview">
              {images.map((img, i) => <img key={i} src={URL.createObjectURL(img)} alt="Preview" />)}
            </div>
          )}
        </div>
      )}

      {step === 5 && (
        <div className="card glass">
          <h2>Owner Contact</h2>
          <label>Owner Name *</label>
          <input name="owner_name" value={form.owner_name} onChange={handleChange} placeholder="Full Name" />

          <label>Owner Phone *</label>
          <input name="owner_phone" value={form.owner_phone} onChange={handleChange} placeholder="Phone Number" />

          <label>Owner Email *</label>
          <input name="owner_email" value={form.owner_email} onChange={handleChange} placeholder="Email" />
        </div>
      )}

      <div className="nav">
        {step > 1 && <button className="btn" onClick={prev}>Back</button>}
        {step < steps.length && <button className="btn" onClick={next}>Next</button>}
        {step === steps.length && <button className="btn submit" onClick={handleSubmit}>Submit Property</button>}
      </div>
    </div>
  );
}

