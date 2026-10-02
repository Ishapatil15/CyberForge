import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import {
  Bell,
  Search,
  User as UserIcon,
  LogOut,
  LayoutDashboard,
  ShieldAlert,
  Users,
  History,
  Menu,
  X,
  Compass,
} from "lucide-react";
import { CyberForgeLogo } from "./CyberForgeLogo";
import { useAuth } from "../hooks/useAuth";
import { Button } from "./ui/Button";

const navLinks = [
  { to: "/", label: "Home" },
  { to: "/challenges", label: "Challenges" },
  { to: "/competitions", label: "Competitions" },
  { to: "/leaderboard", label: "Leaderboard" },
  { to: "/learn", label: "Learn" },
  { to: "/about", label: "About" },
];

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/challenges?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchOpen(false);
      setSearchQuery("");
    }
  };

  const isAdminOrAuthor = user?.role === "ADMIN" || user?.role === "CHALLENGE_AUTHOR";

  return (
    <header className="sticky top-0 z-50 border-b border-forge-border bg-forge-bg/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Left: Brand */}
        <CyberForgeLogo />

        {/* Center: Desktop Navigation */}
        <nav className="hidden md:flex md:items-center md:gap-1 lg:gap-2">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) =>
                `rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-forge-cyan/10 text-forge-cyan"
                    : "text-forge-muted hover:bg-white/5 hover:text-forge-text"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        {/* Right: Actions */}
        <div className="flex items-center gap-3">
          {/* Quick Search Button */}
          <button
            onClick={() => setSearchOpen(!searchOpen)}
            className="rounded-lg p-2 text-forge-muted transition hover:bg-white/5 hover:text-forge-text"
            title="Search challenges"
          >
            <Search className="h-4 w-4" />
          </button>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setNotifOpen(!notifOpen)}
              className="relative rounded-lg p-2 text-forge-muted transition hover:bg-white/5 hover:text-forge-text"
              title="Notifications"
            >
              <Bell className="h-4 w-4" />
              <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-forge-cyan" />
            </button>

            {notifOpen && (
              <div className="absolute right-0 mt-2 w-80 rounded-xl border border-forge-border bg-forge-card p-4 shadow-xl z-50">
                <div className="flex items-center justify-between border-b border-forge-border pb-2.5">
                  <span className="font-heading text-sm font-semibold text-forge-text">Telemetry Alerts</span>
                  <span className="font-mono text-[10px] text-forge-cyan">SYSTEM ONLINE</span>
                </div>
                <div className="mt-3 space-y-2.5 text-xs">
                  <div className="rounded-lg border border-forge-border bg-forge-bg/60 p-2.5">
                    <p className="font-semibold text-forge-text">Cyber Warfare 2026</p>
                    <p className="mt-0.5 text-forge-muted">Competition is live. Submit flags to rank on event leaderboard.</p>
                  </div>
                  <div className="rounded-lg border border-forge-border bg-forge-bg/60 p-2.5">
                    <p className="font-semibold text-forge-text">New Challenge Tracks</p>
                    <p className="mt-0.5 text-forge-muted">Reverse engineering and forensics modules unlocked.</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* User state */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2.5 rounded-lg border border-forge-border bg-forge-card px-2.5 py-1.5 transition hover:border-forge-borderHover"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-md bg-forge-purple/20 text-forge-purple font-mono text-xs font-bold">
                  {user.username.slice(0, 2).toUpperCase()}
                </div>
                <div className="hidden text-left sm:block">
                  <p className="text-xs font-semibold leading-tight text-forge-text">{user.username}</p>
                  <p className="font-mono text-[11px] text-forge-cyan leading-tight">{user.total_points} PTS</p>
                </div>
              </button>

              {profileOpen && (
                <div
                  className="absolute right-0 mt-2 w-56 rounded-xl border border-forge-border bg-forge-card py-1.5 shadow-xl z-50"
                  onClick={() => setProfileOpen(false)}
                >
                  <div className="border-b border-forge-border px-4 py-2">
                    <p className="text-xs text-forge-muted">Signed in as</p>
                    <p className="font-medium text-forge-text">{user.username}</p>
                    <p className="font-mono text-[10px] text-forge-cyan mt-0.5">{user.role}</p>
                  </div>
                  <Link
                    to="/dashboard"
                    className="flex items-center gap-2.5 px-4 py-2 text-sm text-forge-muted hover:bg-white/5 hover:text-forge-text"
                  >
                    <LayoutDashboard className="h-4 w-4" />
                    Dashboard
                  </Link>
                  <Link
                    to="/profile"
                    className="flex items-center gap-2.5 px-4 py-2 text-sm text-forge-muted hover:bg-white/5 hover:text-forge-text"
                  >
                    <UserIcon className="h-4 w-4" />
                    Operator Profile
                  </Link>
                  <Link
                    to="/teams"
                    className="flex items-center gap-2.5 px-4 py-2 text-sm text-forge-muted hover:bg-white/5 hover:text-forge-text"
                  >
                    <Users className="h-4 w-4" />
                    Teams & Squads
                  </Link>
                  <Link
                    to="/submissions"
                    className="flex items-center gap-2.5 px-4 py-2 text-sm text-forge-muted hover:bg-white/5 hover:text-forge-text"
                  >
                    <History className="h-4 w-4" />
                    Submission Log
                  </Link>
                  {isAdminOrAuthor && (
                    <Link
                      to="/admin"
                      className="flex items-center gap-2.5 px-4 py-2 text-sm text-forge-purple hover:bg-forge-purple/10"
                    >
                      <ShieldAlert className="h-4 w-4" />
                      Admin Control
                    </Link>
                  )}
                  <div className="border-t border-forge-border my-1" />
                  <button
                    onClick={async () => {
                      await logout();
                      navigate("/");
                    }}
                    className="flex w-full items-center gap-2.5 px-4 py-2 text-sm text-forge-error hover:bg-forge-error/10"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/login">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link to="/challenges">
                <Button variant="primary" size="sm" className="hidden sm:inline-flex">
                  <Compass className="h-3.5 w-3.5" />
                  Explore Challenges
                </Button>
              </Link>
            </div>
          )}

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="rounded-lg p-2 text-forge-muted md:hidden hover:bg-white/5"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Quick Search Bar Drawer */}
      {searchOpen && (
        <div className="border-t border-forge-border bg-forge-surface px-4 py-3 sm:px-8">
          <form onSubmit={handleSearch} className="mx-auto flex max-w-2xl items-center gap-2">
            <Search className="h-4 w-4 text-forge-cyan" />
            <input
              type="text"
              placeholder="Search challenges by keyword, vulnerability, CVE, tag..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              autoFocus
              className="w-full bg-transparent text-sm text-forge-text placeholder:text-forge-subtle outline-none"
            />
            <Button size="sm" type="submit">
              Search
            </Button>
            <button
              type="button"
              onClick={() => setSearchOpen(false)}
              className="text-xs text-forge-muted hover:text-forge-text"
            >
              Cancel
            </button>
          </form>
        </div>
      )}

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="border-t border-forge-border bg-forge-bg px-4 py-4 md:hidden">
          <nav className="flex flex-col gap-1.5">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === "/"}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-medium ${
                    isActive ? "bg-forge-cyan/10 text-forge-cyan" : "text-forge-muted"
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
            {user && (
              <>
                <div className="border-t border-forge-border my-2" />
                <Link
                  to="/dashboard"
                  onClick={() => setMobileOpen(false)}
                  className="px-3 py-2 text-sm text-forge-muted"
                >
                  Dashboard
                </Link>
                <Link
                  to="/profile"
                  onClick={() => setMobileOpen(false)}
                  className="px-3 py-2 text-sm text-forge-muted"
                >
                  Profile
                </Link>
                <Link
                  to="/teams"
                  onClick={() => setMobileOpen(false)}
                  className="px-3 py-2 text-sm text-forge-muted"
                >
                  Teams
                </Link>
                {isAdminOrAuthor && (
                  <Link
                    to="/admin"
                    onClick={() => setMobileOpen(false)}
                    className="px-3 py-2 text-sm text-forge-purple font-medium"
                  >
                    Admin Control
                  </Link>
                )}
              </>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
