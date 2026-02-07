import { Link } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
export default function Welcome() {
  return (
    <MainLayout>
      <div className="auth-wrapper">
        <div className="auth-card welcome-card">
          <div className="welcome-header">
            <h2 className="welcome-title">
              Welcome to AI Real Estate Assistant
            </h2>

            <p className="welcome-description">
              Intelligent analysis of residential real estate using
              data-driven forecasting and location intelligence.
            </p>
          </div>

          <div className="welcome-actions">
            <Link to="/login" className="welcome-link-button">
              <button className="btn-primary btn-large">
                Login
              </button>
            </Link>

            <div className="welcome-links">
              <Link to="/register" className="welcome-link-secondary">
                Create an account
              </Link>
            </div>

            <div className="welcome-links">
              <Link to="/forgot-password" className="welcome-link-forgot">
                Forgot password?
              </Link>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}