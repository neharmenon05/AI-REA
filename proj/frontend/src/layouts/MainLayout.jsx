import Navbar from "../components/navbar";
import Footer from "../components/Footer";

export default function MainLayout({ children }) {
  return (
    <div className="app-wrapper">
      <Navbar />
      <main>{children}</main>
      <Footer />
    </div>
  );
}
