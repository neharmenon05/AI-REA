export default function Footer() {
  return (
    <footer
      style={{
        marginTop: "auto",
        backgroundColor: "#f9fafb",
        padding: "20px",
        textAlign: "center",
        borderTop: "1px solid #e5e7eb",
        color: "#4b5563",
        fontSize: "14px",
        position: "fixed",
        bottom: 0,
        left: 0,
        width: "100%",
      }}
    >
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        <p>
          © {new Date().getFullYear()} AI Real Estate Assistant. Academic & research use.
        </p>
      </div>
    </footer>
  );
}
