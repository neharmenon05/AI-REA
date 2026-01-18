import MainLayout from "../layouts/MainLayout";
import { supabase } from "../api/supabase";

export default function Register() {
  const register = async (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    const password = e.target.password.value;

    const { error } = await supabase.auth.signUp({
      email,
      password,
    });

    if (!error) {
      alert("Check your email to confirm registration");
    } else {
      alert(error.message);
    }
  };

  return (
    <MainLayout>
      <div className="auth-wrapper">
        <form className="auth-card auth-form" onSubmit={register}>
          <h2 className="auth-title">Create Account</h2>
          <p className="auth-subtitle">Sign up to get started</p>

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
            Register
          </button>

          <div className="auth-links">
            <span>Already have an account?</span>
            <a href="/login" className="auth-link">Login</a>
          </div>
        </form>
      </div>
    </MainLayout>
  );
}
