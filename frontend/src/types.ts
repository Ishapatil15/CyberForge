export type Role = "USER" | "CHALLENGE_AUTHOR" | "ADMIN";

export type User = {
  id: number;
  username: string;
  email: string;
  role: Role;
  avatar_url?: string | null;
  bio?: string | null;
  total_points: number;
  is_active: boolean;
  is_suspended: boolean;
  created_at: string;
};

export type Challenge = {
  id: number;
  title: string;
  slug: string;
  description: string;
  category: string;
  difficulty: string;
  points: number;
  tags: string[];
  author?: string | null;
  flag_format: string;
  solve_count?: number;
  solved?: boolean;
  is_published: boolean;
  created_at: string;
  attachments: { id: number; original_name: string; size_bytes: number }[];
  hint_count?: number;
  competition_ids?: number[];
  hints?: {
    id: number;
    order_index: number;
    cost: number;
    revealed?: boolean;
    content?: string | null;
  }[];
  attempts?: { id: number; is_correct: boolean; created_at: string }[];
};

export type Competition = {
  id: number;
  name: string;
  slug: string;
  description: string;
  rules: string;
  mode: "INDIVIDUAL" | "TEAM";
  status: string;
  start_at: string;
  end_at: string;
  registration_start_at: string;
  registration_end_at: string;
  registration_required: boolean;
  participant_count: number;
  challenge_count: number;
  registered: boolean;
  my_score?: number | null;
  my_rank?: number | null;
  server_now: string;
  challenges?: Challenge[];
};

export type Team = {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  captain_id: number;
  captain?: string | null;
  members: { id: number; username: string; points: number }[];
  points: number;
  solves: number;
  rank?: number | null;
};
