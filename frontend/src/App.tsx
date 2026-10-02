import { Route, Routes } from "react-router-dom";
import { GuestOnly, RequireAuth } from "./components/Guards";
import AppLayout from "./layouts/AppLayout";
import HomePage from "./pages/HomePage";
import LearnPage from "./pages/LearnPage";
import AboutPage from "./pages/AboutPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import ChallengesPage from "./pages/ChallengesPage";
import ChallengeDetailPage from "./pages/ChallengeDetailPage";
import LeaderboardPage from "./pages/LeaderboardPage";
import TeamsPage from "./pages/TeamsPage";
import TeamDetailPage from "./pages/TeamDetailPage";
import CompetitionsPage from "./pages/CompetitionsPage";
import CompetitionDetailPage from "./pages/CompetitionDetailPage";
import SubmissionsPage from "./pages/SubmissionsPage";
import ProfilePage from "./pages/ProfilePage";
import AdminLayout from "./pages/admin/AdminLayout";
import AdminHome from "./pages/admin/AdminHome";
import AdminChallenges from "./pages/admin/AdminChallenges";
import ChallengeEditor from "./pages/admin/ChallengeEditor";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminTeams from "./pages/admin/AdminTeams";
import AdminCompetitions from "./pages/admin/AdminCompetitions";
import AdminSubmissions from "./pages/admin/AdminSubmissions";
import AdminActivity from "./pages/admin/AdminActivity";
import AdminLabs from "./pages/admin/AdminLabs";

export default function App() {
  return (
    <Routes>
      {/* Standalone Auth Pages */}
      <Route element={<GuestOnly />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Pages with CyberForge AppLayout */}
      <Route element={<AppLayout />}>
        {/* Public Discovery Pages */}
        <Route path="/" element={<HomePage />} />
        <Route path="/challenges" element={<ChallengesPage />} />
        <Route path="/challenges/:id" element={<ChallengeDetailPage />} />
        <Route path="/competitions" element={<CompetitionsPage />} />
        <Route path="/competitions/:id" element={<CompetitionDetailPage />} />
        <Route path="/leaderboard" element={<LeaderboardPage />} />
        <Route path="/learn" element={<LearnPage />} />
        <Route path="/about" element={<AboutPage />} />

        {/* Authenticated Operator Pages */}
        <Route element={<RequireAuth />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/teams" element={<TeamsPage />} />
          <Route path="/teams/:id" element={<TeamDetailPage />} />
          <Route path="/submissions" element={<SubmissionsPage />} />
          <Route path="/profile" element={<ProfilePage />} />

          {/* Admin Control Center */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminHome />} />
            <Route path="challenges" element={<AdminChallenges />} />
            <Route path="challenges/new" element={<ChallengeEditor />} />
            <Route path="challenges/:id" element={<ChallengeEditor />} />
            <Route path="labs" element={<AdminLabs />} />
            <Route path="users" element={<AdminUsers />} />
            <Route path="teams" element={<AdminTeams />} />
            <Route path="competitions" element={<AdminCompetitions />} />
            <Route path="submissions" element={<AdminSubmissions />} />
            <Route path="activity" element={<AdminActivity />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}
