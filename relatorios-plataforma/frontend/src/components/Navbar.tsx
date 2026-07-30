import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const roleLabels: Record<string, string> = {
  admin: "Administrador",
  gestor: "Gestor",
  membro: "Membro",
};

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!user) return null;

  return (
    <header className="navbar">
      <div className="navbar-brand">Relatórios</div>
      <nav className="navbar-links">
        <NavLink to="/" end>
          Relatórios
        </NavLink>
        {(user.role === "admin" || user.role === "gestor") && (
          <NavLink to="/admin">Administração</NavLink>
        )}
      </nav>
      <div className="navbar-user">
        <span className="user-badge">{roleLabels[user.role]}</span>
        <span>{user.name}</span>
        <button className="link-button" onClick={handleLogout}>
          Sair
        </button>
      </div>
    </header>
  );
}
