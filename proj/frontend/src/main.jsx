import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import './i18n/i18n';
import "./styles/global.css";
import "./styles/layout.css";
import "./styles/auth.css";
import "./styles/dashboard.css";
import "./styles/buy-property.css";
import "./styles/sell-property.css";
import "./styles/marketplace.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);