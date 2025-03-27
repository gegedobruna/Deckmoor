// src/services/deckService.js
import { doc, setDoc, getDocs, collection, deleteDoc } from 'firebase/firestore';
import { db } from '../firebase/firebase'; // Fixed path

export async function saveDeck(deck) {
  await setDoc(doc(db, "decks", deck.id), deck);
}

export async function loadDecks() {
  const querySnapshot = await getDocs(collection(db, "decks"));
  return querySnapshot.docs.map(doc => doc.data());
}

export async function deleteDeck(deckId) {
  await deleteDoc(doc(db, "decks", deckId));
}