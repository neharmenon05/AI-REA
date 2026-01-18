import MainLayout from "../layouts/MainLayout";
import { supabase } from "../api/supabase";

export default function Login() {
  const login = async (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    const password = e.target.password.value;

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (!error) {
      window.location.href = "/dashboard";
    } else {
      alert(error.message);
    }
  };

  return (
    <MainLayout>
      <div className="auth-wrapper">
        <form className="auth-card auth-form" onSubmit={login}>
          <h2 className="auth-title">Welcome Back</h2>
          <p className="auth-subtitle">Login to access your dashboard</p>

          <div className="form-group">
            <label htmlFor="email" className="form-label">Email Address</label>
            <input
              id="email"
              name="email"
              type="email"
              className="form-input"
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              className="form-input"
              placeholder="Enter your password"
              required
            />
          </div>

          <button type="submit" className="btn-primary auth-button">
            Login
          </button>

          <div className="auth-links">
            <span>Don’t have an account?</span>
            <a href="/register" className="auth-link">Sign up</a>
          </div>
        </form>
      </div>
    </MainLayout>
  );
}
