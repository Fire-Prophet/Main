import React from 'react';
import { Link } from 'react-router-dom';

const NavBar = () => (
  <nav style={{
    display: 'flex', justifyContent: 'space-between',
    padding: '10px 20px', backgroundColor: '#eee'
  }}>
    <Link to="/">🏠 홈</Link>
    <Link to="/map">🗺️ 지도</Link>
  </nav>
);

export default NavBar;
