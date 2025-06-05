import React from 'react';
import './Sidebar.css';

function Sidebar() {
  return (
    <aside className="Sidebar">
      <nav>
        <ul>
          <li><a href="#">Home</a></li>
          <li><a href="#">About</a></li>
          <li><a href="#">Services</a></li>
          <li><a href="#">Contact</a></li>
        </ul>
      </nav>
    </aside>
  );
}

export default Sidebar;
