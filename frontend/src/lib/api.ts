export type Topic = {
  title: string;
  summary: string;
  source_url: string;
  source_name: string;
  competition: string;
  discovered_at: string;
};

const API_URL = process.env.FUTBOL_API_URL ?? "http://localhost:8000";

export async function getTopics(competition?: string): Promise<Topic[]> {
  const url = new URL("/api/topics", API_URL);
  if (competition) url.searchParams.set("competition", competition);

  try {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return [];
    const data = await res.json();
    return data.topics as Topic[];
  } catch {
    return [];
  }
}
