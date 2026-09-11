import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Futbol Gündem",
    short_name: "Futbol",
    start_url: "/",
    display: "standalone",
    background_color: "#0b1210",
    theme_color: "#0b1210",
  };
}
