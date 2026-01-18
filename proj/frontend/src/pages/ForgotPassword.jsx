import MainLayout from "../layouts/MainLayout";
import { supabase } from "../api/supabase";

export default function ForgotPassword() {
  const reset = async (e) => {
    e.preventDefault();
    const email = e.target.email.value;

    const { error } = await supabase.auth.resetPasswordForEmail(email);

    if (!error) alert("Password reset email sent");
    else alert(error.message);
  };

  return (
    <MainLayout>
      <div className="auth-wrapper">
        <form className="auth-card" onSubmit={reset}>
          <h2>Reset Password</h2>

          <input
            name="email"
            type="email"
            placeholder="Email"
            required
          />

          <button>Send Reset Link</button>
        </form>
      </div>
    </MainLayout>
  );
}
