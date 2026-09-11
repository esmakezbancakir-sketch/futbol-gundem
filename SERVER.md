# Futbol VPS — Sunucu Bilgileri

- **Sağlayıcı**: Hetzner Cloud
- **Sunucu adı**: `futbol-vps` (id: 165512507)
- **Tip**: cx23 — 2 vCPU, 4GB RAM, 40GB disk, ~€6.49/ay
- **Lokasyon**: fsn1 (Falkenstein, Almanya)
- **İşletim sistemi**: Ubuntu 24.04
- **IPv4**: 49.13.80.15
- **IPv6**: 2a01:4f8:c010:b2f0::/64
- **SSH key**: `~/.ssh/futbol_hetzner` (private, bu makinede) /
  `~/.ssh/futbol_hetzner.pub` (Hetzner hesabına "futbol-vps" adıyla yüklendi)
- **Root şifresi**: yok — sadece SSH key ile giriş (daha güvenli)
- **Bağlanmak için**: `ssh -i ~/.ssh/futbol_hetzner root@49.13.80.15`
- **Etiket**: `project=futbol` (Hetzner konsolunda filtrelemek için)

Bu sunucu fikirpazar projesiyle **paylaşılmıyor** — futbol sitesine özel,
bağımsız bir kurulum.

## Sıradaki adım
Coolify kurulumu (`curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash`)
ve ardından frontend/backend uygulamalarının bu sunucuya deploy edilmesi.
