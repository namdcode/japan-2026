# 🍁 Japon 2026 — momiji, onsen & ferry vers la Corée

Site compagnon du voyage de groupe **Japon + Corée du Sud**, du **13 novembre au 4 décembre 2026** (21 nuits), à 5, au départ/retour de Paris via Haneda.

**👉 [Voir le site en ligne](https://namdcode.github.io/japan-2026/)**

Tout est dans un seul fichier — [`index.html`](index.html) : une carte plein écran du parcours qu'on déplace et zoome au doigt, et sur laquelle on ouvre chaque étape (logement, jours, programme heure par heure), plus la checklist des réservations restantes et les infos pratiques (saison, transports, logistique à 5). Pensé mobile : les panneaux se replient pour rendre la carte, et le programme d'un jour zoome sur le lieu concerné.

## L'itinéraire en un coup d'œil

```mermaid
flowchart LR
    A["🗼 Tokyo\n4 nuits"] --> B["♨️ Yufuin\nKyushu · 2 nuits"]
    B --> C["🍜 Fukuoka\n2 nuits"]
    C -- "⛴️ ferry" --> D["🇰🇷 Busan\n2 nuits"]
    D -- "🌙 ferry de nuit" --> E["⛩️ Hiroshima\n+ Miyajima · 2 nuits"]
    E --> F["🏮 Okayama\n+ Kurashiki · 1 nuit"]
    F --> G["🐙 Osaka\nKansai · 5 nuits"]
    G --> H["🛫 Tokyo\nretour · 2 nuits"]
```

Le pont férié japonais (21–23 nov, Kinrō Kansha no Hi) est volontairement passé entièrement à Busan pour éviter le pic de foule à Miyajima et Kyoto.

## Statut

Hébergements **confirmés** du 13/11 au 4 déc, aucune nuit manquante. Il reste surtout des réservations d'activités à boucler :

- 🔥 **PokéPark Kanto** (5 billets, lun 16/11) — loterie, fenêtre ≈ mi-août 2026
- 🔥 **Ferry Hakata ⇄ Busan** (Camellia Line) — Economy Bargain, non remboursable
- USJ Express Pass, sièges shinkansen ×5, traductions JAF des permis, minivan Kyushu, restos pour 5

Liste complète et à jour → bouton **À faire** en haut du site.

## Modifier l'itinéraire

`index.html` est la seule source de vérité — pas de doc séparé à maintenir en parallèle. Le contenu vit dans trois tableaux JS en haut du `<script>` :

| Tableau | Contenu |
|---|---|
| `STAGES` | une entrée par étape/ville : dates, logement, notes jour par jour, transition vers l'étape suivante |
| `TODOS` | réservations en attente, avec deadline et flag d'urgence |
| `INFOS` | cartes pratiques (momiji, météo, le coup du férié, transports, logistique à 5) |

Éditer ces tableaux directement, committer, et GitHub Pages republie automatiquement (`main` → live en ~1 min).

Pour du contexte complet (contraintes, décisions passées, préférences de travail), voir [`CLAUDE.md`](CLAUDE.md) — utile si tu demandes à Claude Code de faire les modifications.

## Stack

Un seul fichier HTML, zéro dépendance, zéro build. Hébergé sur GitHub Pages.
