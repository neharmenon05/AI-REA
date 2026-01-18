import MainLayout from "../layouts/MainLayout";

export default function About() {
  return (
    <MainLayout>
      <div className="about-container">
        <div className="about-hero">
          <h1 className="about-title">About AI Real Estate Assistant</h1>
          <p className="about-subtitle">
            Transforming property investment decisions with artificial intelligence
          </p>
        </div>

        <div className="about-content">
          <section className="about-section">
            <h2 className="about-section-title">Our Mission</h2>
            <p className="about-text">
              We empower property investors and buyers with cutting-edge AI technology
              to make informed real estate decisions. Our platform analyzes market trends,
              location intelligence, and risk factors to provide comprehensive property insights.
            </p>
          </section>

          <section className="about-section">
            <h2 className="about-section-title">Key Features</h2>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">📊</div>
                <h3>Price Forecasting</h3>
                <p>AI-powered predictions for property value appreciation over 2, 3, and 5 years</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">🗺️</div>
                <h3>Location Intelligence</h3>
                <p>Comprehensive analysis of nearby amenities, infrastructure, and neighborhood quality</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">⚠️</div>
                <h3>Risk Assessment</h3>
                <p>Detailed evaluation of investment risks and market volatility</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">📰</div>
                <h3>Local News</h3>
                <p>Real-time updates about developments affecting property values in your area</p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2 className="about-section-title">How It Works</h2>
            <div className="steps-container">
              <div className="step-item">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h3>Describe Your Property</h3>
                  <p>Enter details about the property including location, size, and type</p>
                </div>
              </div>
              <div className="step-item">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h3>AI Analysis</h3>
                  <p>Our advanced algorithms analyze market data, trends, and location factors</p>
                </div>
              </div>
              <div className="step-item">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h3>Get Insights</h3>
                  <p>Receive comprehensive reports with pricing, forecasts, and recommendations</p>
                </div>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2 className="about-section-title">Technology</h2>
            <p className="about-text">
              Our platform leverages machine learning models trained on extensive real estate
              datasets, combined with real-time market data and location intelligence APIs.
              We use Google's Gemini AI for natural language processing and advanced
              analytics to deliver accurate, actionable insights.
            </p>
          </section>
        </div>
      </div>
    </MainLayout>
  );
}