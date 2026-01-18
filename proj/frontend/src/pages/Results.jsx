import MainLayout from "../layouts/MainLayout.jsx";
import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const formatCurrency = (v) => typeof v==="number"? `₹ ${v.toLocaleString("en-IN")}`:"Not available";
const formatAddress = (loc) => {
  const comps = loc?.data?.address_components;
  if(!Array.isArray(comps)) return "Not available";
  const pick = t => comps.find(c=>c.types.includes(t))?.long_name;
  return [pick("locality"), pick("administrative_area_level_1"), "India"].filter(Boolean).join(", ");
}

export default function Results(){
  const { state } = useLocation();
  const navigate = useNavigate();
  const query = state?.query;

  const [results,setResults] = useState(null);
  const [loading,setLoading] = useState(true);
  const [amenityCategory,setAmenityCategory] = useState(null);
  const [dark,setDark] = useState(localStorage.getItem("dark")==="true");

  const [newsPage,setNewsPage] = useState(1);
  const NEWS_PAGE_SIZE = 3;
  const loadMoreRef = useRef();

  useEffect(()=>{
    document.body.className = dark?"dark":"";
    localStorage.setItem("dark",dark);
  },[dark]);

  useEffect(()=>{
    if(!query){ navigate("/dashboard"); return; }
    (async()=>{
      try{
        const res = await fetch("http://localhost:8000/api/analyze",{
          method:"POST",
          headers:{"Content-Type":"application/json"},
          body: JSON.stringify({query})
        });
        const data = await res.json();
        setResults(data);
        setAmenityCategory(Object.keys(data.amenities||{})[0]);
      }catch{
        alert("Failed to load analysis.");
      }finally{setLoading(false);}
    })();
  },[query,navigate]);

  // Infinite scroll for news
  useEffect(()=>{
    if(!results?.news?.length) return;
    const observer = new IntersectionObserver(entries=>{
      if(entries[0].isIntersecting){
        setNewsPage(p=>{
          const maxPages = Math.ceil(results.news.length/NEWS_PAGE_SIZE);
          return p<maxPages?p+1:p;
        });
      }
    },{threshold:1});
    if(loadMoreRef.current) observer.observe(loadMoreRef.current);
    return ()=>observer.disconnect();
  },[results?.news]);

  const exportPDF = async ()=>{
    const el = document.getElementById("pdf-area");
    const canvas = await html2canvas(el,{scale:2});
    const img = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p","mm","a4");
    const w=210; const h=(canvas.height*w)/canvas.width;
    pdf.addImage(img,"PNG",0,0,w,h);
    pdf.save("property-analysis.pdf");
  }

  const renderForecast = ()=>{
    const f = results?.forecast;
    if(!f) return <p className="results-muted">Forecast not available.</p>;
    const years=["2","3","5"];
    const data = years.map(y=>({year:`${y} yr`, price:Number(f[y])})).filter(d=>!isNaN(d.price));
    if(!data.length) return <p className="results-muted">Forecast incomplete.</p>;
    return <ResponsiveContainer width="100%" height={160}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3"/>
        <XAxis dataKey="year"/>
        <YAxis tickFormatter={v=>`₹${v.toLocaleString("en-IN")}`}/>
        <Tooltip formatter={v=>`₹${v.toLocaleString("en-IN")}`}/>
        <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={{r:6}}/>
      </LineChart>
    </ResponsiveContainer>;
  }

  if(loading) return (
    <MainLayout>
      <div className="dashboard-container">
        <div className="dashboard-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="dashboard-card skeleton">
              <div className="skeleton-header"></div>
              <div className="skeleton-text"></div>
              <div className="skeleton-text"></div>
              <div className="skeleton-text short"></div>
            </div>
          ))}
        </div>
      </div>
    </MainLayout>
  );

  const visibleNews = (results.news||[]).slice(0, newsPage*NEWS_PAGE_SIZE);

  return (
    <MainLayout>
      <div className="results-container" id="pdf-area">
        <div className="results-top-bar">
          <div className="results-header">
            <button className="back-button" onClick={() => navigate("/dashboard")}>
              Back to Dashboard
            </button>
            <h2 className="results-title">Property Analysis Results</h2>
          </div>
          <div className="results-actions">
            <button className="btn-theme" onClick={()=>setDark(!dark)}>
              {dark ? "☀️" : "🌙"}
            </button>
            <button className="btn-pdf" onClick={exportPDF}>
              ⬇️ Export PDF
            </button>
          </div>
        </div>

        <div className="results-grid">
          {/* Row 1: Estimated Price (left) + Risk Analysis (right) */}
          <div className="dashboard-card summary">
            <h3>Estimated Price</h3>
            <div className="results-price">{formatCurrency(results.estimated_current_price)}</div>
            <p className="results-muted">{results.summary}</p>
          </div>

          <div className="dashboard-card risk">
            <h3>Risk Analysis</h3>
            <p className="results-description">{results.risk}</p>
            <p className="results-muted">{results.risk_explanation}</p>
          </div>

          {/* Row 2: Price Forecast - Full Width */}
          <div className="dashboard-card forecast results-full-width">
            <h3>Price Forecast</h3>
            <div className="chart-wrapper">
              {renderForecast()}
            </div>
          </div>

          {/* Row 3: Location (left) + Map View (right) */}
          <div className="dashboard-card location">
            <h3>Location</h3>
            <p className="results-description">{formatAddress(results.location)}</p>
            <p className="results-muted">{results.location?.lat}, {results.location?.lng}</p>
          </div>

          <div className="dashboard-card location">
            <h3>Map View</h3>
            <iframe 
              className="results-map" 
              src={`https://www.google.com/maps?q=${results.location?.lat},${results.location?.lng}&z=15&output=embed`} 
              title="map"
            />
          </div>

          {/* Row 4: Amenities - Full Width */}
          <div className="dashboard-card summary results-full-width">
            <h3>Nearby Amenities</h3>
            <div className="amenities-tabs">
              {Object.keys(results.amenities||{}).map(c=>(
                <button 
                  key={c} 
                  className={`amenity-tab ${amenityCategory===c?"active":""}`} 
                  onClick={()=>setAmenityCategory(c)}
                >
                  {c}
                </button>
              ))}
            </div>
            <div className="amenities-table-wrapper">
              <table className="amenities-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Name</th>
                    <th>Address</th>
                  </tr>
                </thead>
                <tbody>
                  {(results.amenities?.[amenityCategory]?.places||[]).map((p,i)=>(
                    <tr key={i}>
                      <td>{i+1}</td>
                      <td>{p.name}</td>
                      <td className="results-muted">{p.vicinity||p.address}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Row 5: News - Full Width */}
          <div className="dashboard-card forecast results-full-width">
            <h3>Local News & Updates</h3>
            <div className="news-vertical">
              {visibleNews.map((n,i)=>(
                <div className="news-item" key={i}>
                  {"error" in n ? <p className="news-error">{n.error}</p> :
                   "note" in n ? <p className="results-muted">{n.note}</p> :
                   <>
                     <h4 className="news-title">{n.title}</h4>
                     <p className="news-snippet">{n.snippet}</p>
                     <span className="news-source">{n.source}</span>
                   </>}
                </div>
              ))}
              <div ref={loadMoreRef}></div>
            </div>
          </div>

          {/* Row 6: AI Explanation - Full Width */}
          <div className="dashboard-card summary results-full-width">
            <h3>AI Analysis Explanation</h3>
            <p className="results-description">{results.explanation}</p>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}