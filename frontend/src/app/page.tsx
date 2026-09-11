import { getTopics } from "@/lib/api";
import { TopicCard } from "@/components/TopicCard";

export const revalidate = 300;

export default async function HomePage() {
  const topics = await getTopics();

  return (
    <main className="flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold">Futbol Gündem</h1>
        <p className="text-[var(--muted)]">
          Global futboldaki popüler konular otomatik taranıp özetlenir — her
          kart orijinal kaynağa bağlanır.
        </p>
      </header>

      {topics.length === 0 ? (
        <p className="text-[var(--muted)]">
          Henüz içerik yok — ilk tarama döngüsü tamamlandığında burada
          görünecek.
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {topics.map((topic) => (
            <TopicCard key={topic.source_url} topic={topic} />
          ))}
        </div>
      )}
    </main>
  );
}
