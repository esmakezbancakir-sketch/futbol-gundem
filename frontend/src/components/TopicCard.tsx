import type { Topic } from "@/lib/api";

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString("tr-TR", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function TopicCard({ topic }: { topic: Topic }) {
  return (
    <article className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between gap-3 text-xs text-[var(--muted)]">
        <span className="uppercase tracking-wide text-[var(--accent)]">
          {topic.competition || "Futbol"}
        </span>
        <span>{formatDate(topic.discovered_at)}</span>
      </div>
      <h2 className="text-lg font-semibold leading-snug">{topic.title}</h2>
      <p className="text-sm text-[var(--muted)] leading-relaxed">{topic.summary}</p>
      <a
        href={topic.source_url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-sm text-[var(--accent)] hover:underline mt-auto"
      >
        {topic.source_name} — kaynağa git &rarr;
      </a>
    </article>
  );
}
