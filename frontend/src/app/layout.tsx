import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Futbol Gündem",
  description: "Global futboldaki popüler gündem, otomatik özetlenip anlık takip edilir.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body className="min-h-screen antialiased">
        <div className="max-w-5xl mx-auto px-4 py-10">{children}</div>
      </body>
    </html>
  );
}
