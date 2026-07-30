import { useEffect, useState, type FormEvent } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Role, Team, User } from "../types";

const roleLabels: Record<Role, string> = {
  admin: "Administrador",
  gestor: "Gestor",
  membro: "Membro",
};

export default function Admin() {
  const { user: currentUser } = useAuth();
  const isAdmin = currentUser?.role === "admin";

  const [teams, setTeams] = useState<Team[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [teamName, setTeamName] = useState("");

  const [newUser, setNewUser] = useState({
    name: "",
    email: "",
    password: "",
    role: "membro" as Role,
    team_id: "",
  });

  const load = async () => {
    const [teamsRes, usersRes] = await Promise.all([
      api.get<Team[]>("/teams"),
      api.get<User[]>("/users"),
    ]);
    setTeams(teamsRes.data);
    setUsers(usersRes.data);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreateTeam = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.post("/teams", { name: teamName });
      setTeamName("");
      await load();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Erro ao criar time.");
    }
  };

  const handleCreateUser = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.post("/users", {
        ...newUser,
        team_id: newUser.team_id ? Number(newUser.team_id) : null,
      });
      setNewUser({ name: "", email: "", password: "", role: "membro", team_id: "" });
      await load();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Erro ao criar usuário.");
    }
  };

  const handleRoleChange = async (userId: number, role: Role) => {
    await api.patch(`/users/${userId}`, { role });
    await load();
  };

  const handleTeamChange = async (userId: number, team_id: string) => {
    await api.patch(`/users/${userId}`, { team_id: team_id ? Number(team_id) : null });
    await load();
  };

  const handleToggleActive = async (u: User) => {
    await api.patch(`/users/${u.id}`, { is_active: !u.is_active });
    await load();
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm("Remover este usuário?")) return;
    await api.delete(`/users/${userId}`);
    await load();
  };

  const handleDeleteTeam = async (teamId: number) => {
    if (!confirm("Remover este time? Usuários vinculados perderão o time.")) return;
    try {
      await api.delete(`/teams/${teamId}`);
      await load();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Erro ao remover time.");
    }
  };

  return (
    <div className="page">
      {error && <div className="error-box">{error}</div>}

      {isAdmin && (
        <section className="card">
          <h2>Times</h2>
          <form className="inline-form" onSubmit={handleCreateTeam}>
            <input
              placeholder="Nome do time"
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              required
            />
            <button type="submit">Criar time</button>
          </form>
          <ul className="simple-list">
            {teams.map((t) => (
              <li key={t.id}>
                <span>{t.name}</span>
                <button className="link-button danger" onClick={() => handleDeleteTeam(t.id)}>
                  Remover
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {isAdmin && (
        <section className="card">
          <h2>Novo usuário</h2>
          <form className="upload-form" onSubmit={handleCreateUser}>
            <div className="form-row">
              <div className="form-field">
                <label>Nome</label>
                <input
                  value={newUser.name}
                  onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-field">
                <label>Email</label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  required
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-field">
                <label>Senha inicial</label>
                <input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  required
                />
              </div>
              <div className="form-field">
                <label>Papel</label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({ ...newUser, role: e.target.value as Role })}
                >
                  <option value="membro">Membro</option>
                  <option value="gestor">Gestor</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>
              <div className="form-field">
                <label>Time</label>
                <select
                  value={newUser.team_id}
                  onChange={(e) => setNewUser({ ...newUser, team_id: e.target.value })}
                >
                  <option value="">Sem time</option>
                  {teams.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <button type="submit">Criar usuário</button>
          </form>
        </section>
      )}

      <section className="card">
        <h2>Usuários</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Email</th>
              <th>Papel</th>
              <th>Time</th>
              <th>Status</th>
              {isAdmin && <th></th>}
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.name}</td>
                <td>{u.email}</td>
                <td>
                  {isAdmin ? (
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value as Role)}
                    >
                      <option value="membro">Membro</option>
                      <option value="gestor">Gestor</option>
                      <option value="admin">Administrador</option>
                    </select>
                  ) : (
                    roleLabels[u.role]
                  )}
                </td>
                <td>
                  {isAdmin ? (
                    <select
                      value={u.team_id ?? ""}
                      onChange={(e) => handleTeamChange(u.id, e.target.value)}
                    >
                      <option value="">Sem time</option>
                      {teams.map((t) => (
                        <option key={t.id} value={t.id}>
                          {t.name}
                        </option>
                      ))}
                    </select>
                  ) : (
                    teams.find((t) => t.id === u.team_id)?.name ?? "-"
                  )}
                </td>
                <td>{u.is_active ? "Ativo" : "Desativado"}</td>
                {isAdmin && (
                  <td className="table-actions">
                    <button className="link-button" onClick={() => handleToggleActive(u)}>
                      {u.is_active ? "Desativar" : "Ativar"}
                    </button>
                    {u.id !== currentUser?.id && (
                      <button
                        className="link-button danger"
                        onClick={() => handleDeleteUser(u.id)}
                      >
                        Remover
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
