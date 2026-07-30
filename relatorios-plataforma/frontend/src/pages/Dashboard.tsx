import { useEffect, useState, type FormEvent } from "react";
import { api, API_URL } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Report, Team } from "../types";

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("pt-BR");
}

export default function Dashboard() {
  const { user } = useAuth();
  const [reports, setReports] = useState<Report[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [teamFilter, setTeamFilter] = useState<string>("");

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const loadReports = async (team_id?: string) => {
    setLoading(true);
    try {
      const { data } = await api.get<Report[]>("/reports", {
        params: team_id ? { team_id } : {},
      });
      setReports(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
    if (user?.role === "admin") {
      api.get<Team[]>("/teams").then(({ data }) => setTeams(data));
    }
  }, [user]);

  const handleFilterChange = (value: string) => {
    setTeamFilter(value);
    loadReports(value || undefined);
  };

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setUploadError(null);
    try {
      const form = new FormData();
      form.append("title", title);
      form.append("description", description);
      form.append("file", file);
      await api.post("/reports", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setTitle("");
      setDescription("");
      setFile(null);
      (document.getElementById("file-input") as HTMLInputElement).value = "";
      await loadReports(teamFilter || undefined);
    } catch (err: any) {
      setUploadError(err?.response?.data?.detail ?? "Erro ao enviar relatório.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Tem certeza que deseja excluir este relatório?")) return;
    await api.delete(`/reports/${id}`);
    await loadReports(teamFilter || undefined);
  };

  const handleDownload = (id: number) => {
    const token = localStorage.getItem("token");
    fetch(`${API_URL}/reports/${id}/download`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.blob())
      .then((blob) => {
        const report = reports.find((r) => r.id === id);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = report?.original_filename ?? "relatorio";
        a.click();
        window.URL.revokeObjectURL(url);
      });
  };

  return (
    <div className="page">
      <section className="card">
        <h2>Enviar novo relatório</h2>
        <form className="upload-form" onSubmit={handleUpload}>
          <div className="form-row">
            <div className="form-field">
              <label>Título</label>
              <input value={title} onChange={(e) => setTitle(e.target.value)} required />
            </div>
            <div className="form-field">
              <label>Arquivo</label>
              <input
                id="file-input"
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                required
              />
            </div>
          </div>
          <div className="form-field">
            <label>Descrição (opcional)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
            />
          </div>
          {uploadError && <div className="error-box">{uploadError}</div>}
          <button type="submit" disabled={uploading}>
            {uploading ? "Enviando..." : "Enviar relatório"}
          </button>
        </form>
      </section>

      <section className="card">
        <div className="card-header">
          <h2>Relatórios</h2>
          {user?.role === "admin" && (
            <select value={teamFilter} onChange={(e) => handleFilterChange(e.target.value)}>
              <option value="">Todos os times</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {loading ? (
          <p className="muted">Carregando...</p>
        ) : reports.length === 0 ? (
          <p className="muted">Nenhum relatório encontrado.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Título</th>
                <th>Arquivo</th>
                <th>Enviado por</th>
                <th>Time</th>
                <th>Tamanho</th>
                <th>Data</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.id}>
                  <td>
                    <div className="report-title">{r.title}</div>
                    {r.description && <div className="report-desc">{r.description}</div>}
                  </td>
                  <td>{r.original_filename}</td>
                  <td>{r.owner_name}</td>
                  <td>{r.team_name}</td>
                  <td>{formatSize(r.size_bytes)}</td>
                  <td>{formatDate(r.created_at)}</td>
                  <td className="table-actions">
                    <button className="link-button" onClick={() => handleDownload(r.id)}>
                      Baixar
                    </button>
                    {(user?.role === "admin" ||
                      user?.role === "gestor" ||
                      user?.id === r.owner_id) && (
                      <button className="link-button danger" onClick={() => handleDelete(r.id)}>
                        Excluir
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
