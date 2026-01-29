import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="sidebar">
      <NavLink to="/chat" className="icon">
        🤖
      </NavLink>

      <NavLink to="/chat" className="icon">
        💬
      </NavLink>

      <NavLink to="/customers" className="icon">
        👥
      </NavLink>

      <NavLink to="/agents" className="icon">
        ⚙️
      </NavLink>

      <NavLink to="/activity" className="icon">
        📜
      </NavLink>
    </div>
  );
}
