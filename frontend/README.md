# 🃏 Deckmoor — A Commander Deckbuilder & Playtester

**Deckmoor** (originally submitted as `mtg-deckbuilder`) is a Magic: The Gathering web application focused on **Commander (EDH)** deck construction, playtesting, and customization. It was developed as part of a **bachelor's thesis project** at the **University of Debrecen**, combining modern frontend technology with flavorful, immersive design.

This tool blends powerful search features, in-browser testing, and a soft, lore-inspired UI to offer a polished brewing experience for casual and competitive players alike.

---

## 🎓 Academic Acknowledgment

> This application was created as a thesis project at the **University of Debrecen, Faculty of Informatics**, under the supervision of [**Dr. Vágner Anikó Szilvia**](https://inf.unideb.hu/en/people/aniko.vagner).

Author: **Gegë Dobruna**  
Program: BSc in Computer Science  
Graduation: 2025

---

## ✨ Features

- 🔍 Real-time **Scryfall-powered card search** via **FastAPI**
- 🎴 Filter by type, color identity, and set
- 🛠️ Intuitive **deckbuilding interface**, with legality check and renaming features
- 💾 **Firebase** integration for saving decks
- 🧪 **Playtest mode** with draw, shuffle, and simulated gameplay
- 📤 **Import/export** decks via plaintext
- 🎨 Custom Deckmoor logo

---

## ⚠️ Public Database Notice

This project uses an **open-access Firebase Firestore database** with **no authentication**.

All decks are:
- Publicly visible
- Shared between all users
- Not protected from edits or deletion

This is intended as a **demo/test project** and not for storing permanent or private content. Please do not submit sensitive data.

## 🛠️ Stack & Tools

| Tool | Purpose |
|------|---------|
| Vue 3 + Vite | Core frontend stack |
| Firebase | Cloud Firestore database |
| Scryfall API | Card data & search |
| Axios | API calls |
| Chart.js + vue-chartjs | Card stats visualizations |
| mana-font | Mana symbol rendering |
| vue3-notification | Toast messages |

---

## 🖼️ UI Theme

The app is themed around **Deckmoor**, a fictional MTG-inspired glen with a **custom logo**, and elegant serif typography.

Logo and visuals are stored in:
```
src/assets/logo/logo1.png
```
---

## 📦 Install & Run

```bash
git clone https://github.com/gegedobruna/mtg-deckbuilder.git
cd mtg-deckbuilder
npm install
npm run dev
```

> Use `npm run serve` if launching via Vue CLI.

---

## 📁 Project Structure

```
Frontend
src/
├── assets/
│   ├── cards/
│   ├── fonts/
│   ├── icons/
│   ├── mana-master/
│   ├── logo/               
│   └── global.css              
│
├── components/
│   ├── CardSearch.vue    
│   ├── DeckSidebar.vue    
│   └── CardGrid.vue, Popups, etc.
├── App.vue, main.js
├── firebase.js
....
```

---

## 🧪 Playtest Mode

Click the “Playtest” button in the sidebar to:

- Draw hands
- Mulligan and shuffle
- Simulate turn draws
- Add cards directly to zones

Useful for testing curve, synergy, and color balance.

---

## 🧱 License

This codebase is distributed for **educational and personal use** as part of an academic project at the **University of Debrecen**.  
If reused, please retain attribution to:

- **Gegë Dobruna** (author)  
- **Dr. Vágner Anikó Szilvia** (supervisor)  
- **University of Debrecen**

You may modify and share under the terms of the [MIT License](https://opensource.org/licenses/MIT), but please credit the original author and academic context if used in a published or commercial form.

---

## 👤 Author

**Gegë Dobruna**  
GitHub: [@gegedobruna](https://github.com/gegedobruna)

> *“Decks are born in the glens, sharpened in the swamps.”*

---

## 🙌 Special Thanks

- To **Dr. Vágner Anikó Szilvia**, for academic mentorship and encouragement.
- To the **MTG community**, for inspiring the obsession.
- To **Scryfall**, for making free card data so beautifully accessible.

---

## 📮 Feedback & Contributions

Pull requests and feedback are welcome. For serious contributions or future forks, feel free to reach out via GitHub Issues.
