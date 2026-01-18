import { Link } from "react-router-dom";
import { supabase } from "../api/supabase";
import { useAuth } from "../auth/AuthContext";

export default function Navbar() {
  const { user } = useAuth();

  const logout = async () => {
    await supabase.auth.signOut();
    window.location.href = "/";
  };

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <Link to={user ? "/dashboard" : "/"} className="navbar-title">
          AI-REA
        </Link>

        <div className="nav-links">
          {user ? (
            <>
              <Link to="/dashboard" className="nav-link">Dashboard</Link>
              <Link to="/about" className="nav-link">About</Link>
              <button onClick={logout} className="btn-logout">Logout</button>
            </>
          ) : (
            <>
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/about" className="nav-link">About</Link>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="nav-link nav-link-register">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}