import React from "react";
import "../styles/Header.css";
import logo from '../assets/logo.svg'

function Header() {
  return (
    <header className="header">
      <div className="logo-container">
        <img src={logo} alt="CheatSniper Logo" className="logo" />
        <h1 className="app-name">CheatSniper</h1>
      </div>

      <p className="slogan">"Precision in Detection, Integrity in Action"</p>

      <nav className="nav-links">
        <a href="#">Home</a>
        <a href="#">Features</a>
        <a href="#">About</a>
        <a href="#">Contact</a>
      </nav>
    </header>
  );
}

export default Header;
