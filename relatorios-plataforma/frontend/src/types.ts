export type Role = "admin" | "gestor" | "membro";

export interface Team {
  id: number;
  name: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
  role: Role;
  team_id: number | null;
  is_active: number;
}

export interface Report {
  id: number;
  title: string;
  description: string | null;
  original_filename: string;
  content_type: string | null;
  size_bytes: number;
  owner_id: number;
  team_id: number;
  created_at: string;
  owner_name: string | null;
  team_name: string | null;
}
