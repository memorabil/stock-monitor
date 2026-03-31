# 📦 Stock Monitor — SpringFarma

Monitorizare automată zilnică a stocurilor cu calendar vizual.

## Structura proiectului

```
stock-monitor/
├── .github/
│   └── workflows/
│       └── check-stocks.yml    ← GitHub Actions (rulează zilnic)
├── data/
│   ├── products.json           ← Lista de produse de monitorizat
│   └── history.json            ← Istoricul zilnic al stocurilor
├── web/
│   └── index.html              ← Aplicația web (calendar vizual)
├── check_stocks.py             ← Scriptul Python de verificare
└── README.md
```

---

## Setup pas cu pas

### 1. Creează repository-ul pe GitHub
1. Mergi pe [github.com](https://github.com) și autentifică-te
2. Click **New repository**
3. Nume: `stock-monitor`
4. Setează-l ca **Public** (necesar pentru GitHub Pages)
5. Click **Create repository**

### 2. Urcă fișierele
Poți face asta direct din browser pe GitHub:
- Click **Add file → Upload files**
- Urcă toate fișierele din acest arhivă menținând structura de directoare

### 3. Adaugă produsele de monitorizat
Editează `data/products.json` și înlocuiește exemplul cu produsele reale:

```json
[
  {
    "id": "prod1",
    "url": "https://www.springfarma.com/url-produs-1",
    "name": "Numele Produsului 1",
    "status": "unknown",
    "lastCheck": null,
    "lastChanged": null
  },
  {
    "id": "prod2",
    "url": "https://www.springfarma.com/url-produs-2",
    "name": "Numele Produsului 2",
    "status": "unknown",
    "lastCheck": null,
    "lastChanged": null
  }
]
```

**Important:** `id` trebuie să fie unic pentru fiecare produs.

### 4. Activează GitHub Pages
1. Settings → Pages
2. Source: **Deploy from a branch**
3. Branch: `main`, Folder: `/web`
4. Click **Save**

Aplicația va fi disponibilă la:
`https://YOUR_USERNAME.github.io/stock-monitor/`

### 5. Configurează aplicația web
Editează `web/index.html` și înlocuiește la linia ~177:
```js
const GITHUB_USER = "YOUR_GITHUB_USERNAME";  // ← pune username-ul tău
const GITHUB_REPO = "stock-monitor";
```

### 6. Testează manual
1. Mergi la tab-ul **Actions** din repo
2. Click pe workflow-ul **Check Stock Daily**
3. Click **Run workflow → Run workflow**
4. Aşteaptă ~1 minut și verifică că `data/history.json` s-a actualizat

---

## Cum funcționează

```
GitHub Actions (08:00 zilnic)
        ↓
check_stocks.py rulează
        ↓
Accesează fiecare URL din products.json
        ↓
Caută "ÎN STOC" sau "INDISPONIBIL" în pagină
        ↓
Salvează rezultatul în data/history.json
        ↓
Commit automat în repository
        ↓
web/index.html citește datele și afișează calendarul
```

---

## Adăugare produse noi

Editează `data/products.json` direct pe GitHub și adaugă un nou obiect în array. La următoarea rulare (sau manual din Actions), produsul va fi verificat automat.

---

## Frecvență verificare

Implicit: **08:00 ora României (06:00 UTC)** zilnic.

Modifică în `.github/workflows/check-stocks.yml`:
```yaml
- cron: '0 6 * * *'   # 06:00 UTC = 08:00 EET (iarna) / 09:00 EEST (vara)
```

---

## Depanare

**GitHub Actions eșuează?**
- Verifică tab-ul Actions pentru log-uri
- Asigură-te că `permissions: contents: write` este în workflow

**Pagina web nu se încarcă datele?**
- Verifică că `GITHUB_USER` e setat corect în `web/index.html`
- Repo-ul trebuie să fie **Public**
- Verifică consola browser-ului (F12) pentru erori CORS
