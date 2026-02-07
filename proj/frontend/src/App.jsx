import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import AutoTranslate from "./components/AutoTranslate";
import LanguageSwitcher from "./components/LanguageSwitcher";

import Welcome from "./pages/Welcome";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import Results from "./pages/Results";
import About from "./pages/About";
import Marketplace from "./pages/Marketplace";
import SellProperty from "./pages/SellProperty";
import BuyProperty from "./pages/BuyProperty";
import Assistant from "./components/Assistant";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <div />; // prevents blank screen flicker
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AutoTranslate>
          {/* Language Switcher */}
          <div
            style={{
              position: "fixed",
              top: "20px",
              right: "20px",
              zIndex: 10000,
            }}
          >
            <LanguageSwitcher />
          </div>

          <Routes>
            <Route path="/" element={<Welcome />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/about" element={<About />} />

            {/* FIXED: Add leading slash */}
            <Route path="/marketplace" element={<Marketplace />} />
            <Route path="/marketplace/sell" element={<SellProperty />} />
            <Route path="/marketplace/buy" element={<BuyProperty />} />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="/results"
              element={
                <ProtectedRoute>
                  <Results />
                </ProtectedRoute>
              }
            />

            {/* Optional fallback route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>

          {/* Assistant should be outside Routes but inside Router */}
          <Assistant />
        </AutoTranslate>
      </BrowserRouter>
    </AuthProvider>
  );
}
