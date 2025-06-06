
# 🃏 Deckmoor — A Commander Deckbuilder & Playtester

**Deckmoor** (originally submitted as `mtg-deckbuilder`) is a Magic: The Gathering web application focused on **Commander (EDH)** deck construction, playtesting, and customization. It was developed as part of a **bachelor's thesis project** at the **University of Debrecen**, combining modern frontend technology with flavorful, immersive design.

The app blends powerful **Scryfall search**, **Firebase deck storage**, and a smooth, lore-inspired interface to offer a polished brewing experience for casual and competitive players alike.

---

## 🎓 Academic Acknowledgment

> This application was created as a thesis project at the **University of Debrecen, Faculty of Informatics**, under the supervision of [**Dr. Vágner Anikó Szilvia**](https://inf.unideb.hu/dr-vagner-aniko-szilvia).

Author: **Gegë Dobruna**  
Program: BSc in Computer Science  
Graduation: 2025

---

## ✨ Features

- 🔍 **FastAPI-powered search** using real-time **Scryfall data**
- 🎴 Filter by card type, set, mana cost, and color identity
- 🛠️ Intuitive **deckbuilder interface** with legality checks and renaming
- 💾 **Firebase** Firestore integration for deck saving
- 🧪 Fully featured **playtest mode**
- 📤 Import/export decks via plaintext or clipboard
- 🌐 Hosted with a **Vue frontend on GitHub Pages** and a **Python backend on Render**
- 🎨 Custom logo, fonts, and MTG-style UI

---

## 🌐 Live Deployment

- **Frontend:** [deckmoor GitHub Pages](https://gegedobruna.github.io/Deckmoor)
- **Backend:** [deckmoor backend on Render](https://deckmoor.onrender.com)

> You can now use the app end-to-end — no local backend required!

---

## ⚠️ Database Notice

The current Firestore database is **open access with no authentication**.  
All saved decks are:

- Publicly viewable
- Editable by any user
- Not permanent or secure

Use for demo/testing only. Avoid storing sensitive or personal data.

---

## 🛠️ Stack & Tools

| Tool | Purpose |
|------|---------|
| Vue 3 + Vite | Frontend SPA |
| FastAPI | Python backend / API |
| Firebase | Cloud Firestore database |
| Scryfall API | MTG card data |
| Axios | API requests |
| Chart.js + vue-chartjs | Stats visualizations |
| mana-font | MTG mana symbol rendering |
| vue3-notification | Toast messages |

---

## 🖼️ Theme & Visuals

The app is themed around **Deckmoor**, a fictional MTG-inspired glen.  
It uses serif typography and gentle colors to evoke a sense of storybook calm and focus.

Logo stored at:
```
src/assets/logo/logo1.png
```

---

## 📦 Install & Run Locally

```bash
git clone https://github.com/gegedobruna/mtg-deckbuilder.git
cd mtg-deckbuilder
npm install
npm run dev
```

> For backend, run the FastAPI app in the `backend` folder on port `8000`.

---

## 📁 Project Structure (Frontend)

```
src/
├── assets/
│   ├── logo/, fonts/, icons/, mana/, global.css
├── components/
│   ├── CardSearch.vue, DeckSidebar.vue, etc.
├── firebase.js
├── App.vue, main.js
```

---

## 🧪 Playtest Mode

Click **“Playtest”** to:

- Draw opening hands
- Shuffle, mulligan, draw per turn
- Simulate card zones (hand, battlefield, etc.)
- Test mana curve and deck feel

---

## 📜 License

Distributed under the **MIT License** for educational and personal use.  
If you reuse or fork this project:

- Credit **Gegë Dobruna** (author)  
- Credit **University of Debrecen** and **Dr. Vágner Anikó Szilvia** (supervisor)

---

## 👤 Author

**Gegë Dobruna**  
GitHub: [@gegedobruna](https://github.com/gegedobruna)

> *“Decks are born in the glens, sharpened in the swamps.”*

---

## 🙌 Thanks

- **Dr. Vágner Anikó Szilvia** — for mentorship and guidance  
- **MTG community** — for endless inspiration  
- **Scryfall** — for amazing free card data

---

## 📮 Feedback & Contributions

Open to feedback, issues, and pull requests.  
Feel free to fork the repo or [open an issue](https://github.com/gegedobruna/Deckmoor/issues) if you'd like to help shape Deckmoor’s next phase.
