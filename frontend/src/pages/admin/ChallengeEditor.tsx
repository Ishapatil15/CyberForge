import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, ApiError } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input, Label, Select, Textarea } from "../../components/ui/Field";
import { Alert, Loading } from "../../components/ui/Feedback";

const categories = [
  "WEB",
  "CRYPTOGRAPHY",
  "FORENSICS",
  "REVERSE_ENGINEERING",
  "OSINT",
  "STEGANOGRAPHY",
  "BINARY_EXPLOITATION",
  "NETWORKING",
  "MOBILE",
  "MISCELLANEOUS",
];

export default function ChallengeEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const editing = Boolean(id);
  const [loading, setLoading] = useState(editing);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("WEB");
  const [difficulty, setDifficulty] = useState("EASY");
  const [points, setPoints] = useState(100);
  const [tags, setTags] = useState("");
  const [flag, setFlag] = useState("");
  const [flagFormat, setFlagFormat] = useState("CTF{...}");
  const [hints, setHints] = useState("10|Look at the notes");
  const [published, setPublished] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [competitionId, setCompetitionId] = useState("");
  const [competitions, setCompetitions] = useState<{ id: number; name: string }[]>([]);

  useEffect(() => {
    api.get<{ items: { id: number; name: string }[] }>("/api/competitions").then((d) => setCompetitions(d.items)).catch(() => undefined);
    if (id) {
      api.get<Record<string, unknown>>(`/api/admin/challenges/${id}`).then((c) => {
        setTitle(String(c.title || ""));
        setSlug(String(c.slug || ""));
        setDescription(String(c.description || ""));
        setCategory(String(c.category || "WEB"));
        setDifficulty(String(c.difficulty || "EASY"));
        setPoints(Number(c.points || 100));
        setTags(((c.tags as string[]) || []).join(", "));
        setFlagFormat(String(c.flag_format || "CTF{...}"));
        setPublished(Boolean(c.is_published));
        const comps = (c.competition_ids as number[]) || [];
        if (comps.length > 0) setCompetitionId(String(comps[0]));
        const hs = (c.hints as { cost: number; content?: string }[]) || [];
        setHints(hs.map((h) => `${h.cost}|${h.content || ""}`).join("\n"));
        setLoading(false);
      });
    }
  }, [id]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    const hintRows = hints
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line, i) => {
        const [cost, ...rest] = line.split("|");
        return { cost: Number(cost || 0), content: rest.join("|") || cost, order_index: i + 1 };
      });
    const payload: Record<string, unknown> = {
      title,
      slug,
      description,
      category,
      difficulty,
      points: Number(points),
      tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
      flag_format: flagFormat,
      hints: hintRows,
      is_published: published,
      competition_id: competitionId ? Number(competitionId) : null,
    };
    try {
      let challengeId = id;
      if (editing) {
        if (flag) payload.flag = flag;
        await api.patch(`/api/admin/challenges/${id}`, payload);
      } else {
        payload.flag = flag;
        const created = await api.post<{ id: number }>("/api/admin/challenges", payload);
        challengeId = String(created.id);
      }
      if (file && challengeId) {
        await api.upload(`/api/admin/challenges/${challengeId}/attachments`, file);
      }
      navigate("/admin/challenges");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Save failed");
    }
  }

  if (loading) return <Loading />;

  return (
    <Card>
      <form className="grid gap-4" onSubmit={onSubmit}>
        {error && <Alert>{error}</Alert>}
        <div className="grid gap-4 md:grid-cols-2">
          <div><Label>Challenge name</Label><Input value={title} onChange={(e) => setTitle(e.target.value)} required /></div>
          <div><Label>Slug</Label><Input value={slug} onChange={(e) => setSlug(e.target.value)} required /></div>
        </div>
        <div><Label>Description</Label><Textarea value={description} onChange={(e) => setDescription(e.target.value)} required /></div>
        <div className="grid gap-4 md:grid-cols-4">
          <div><Label>Category</Label><Select value={category} onChange={(e) => setCategory(e.target.value)}>{categories.map((c) => <option key={c}>{c}</option>)}</Select></div>
          <div>
            <Label>Difficulty</Label>
            <Select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              <option>EASY</option><option>MEDIUM</option><option>HARD</option><option>EXPERT</option>
            </Select>
          </div>
          <div><Label>Points</Label><Input type="number" value={points} onChange={(e) => setPoints(Number(e.target.value))} /></div>
          <div>
            <Label>Competition</Label>
            <Select value={competitionId} onChange={(e) => setCompetitionId(e.target.value)}>
              <option value="">None / practice</option>
              {competitions.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </Select>
          </div>
        </div>
        <div><Label>Tags</Label><Input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="sql, authentication" /></div>
        <div className="grid gap-4 md:grid-cols-2">
          <div><Label>{editing ? "Flag (leave blank to keep)" : "Flag"}</Label><Input value={flag} onChange={(e) => setFlag(e.target.value)} required={!editing} /></div>
          <div><Label>Flag format</Label><Input value={flagFormat} onChange={(e) => setFlagFormat(e.target.value)} /></div>
        </div>
        <div><Label>Hints (one per line: cost|text)</Label><Textarea value={hints} onChange={(e) => setHints(e.target.value)} /></div>
        <div>
          <Label>Attachment</Label>
          <Input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={published} onChange={(e) => setPublished(e.target.checked)} />
          Published
        </label>
        <Button>{editing ? "Save changes" : "Create challenge"}</Button>
      </form>
    </Card>
  );
}
