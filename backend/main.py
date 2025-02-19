from fastapi import FastAPI, Query
import requests
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
SCRYFALL_URL = "https://api.scryfall.com/cards/search"

@app.get("/")
def read_root():
    return {"message": "Welcome to the MTG Deckbuilder API! Use /search to search for cards."}


@app.get("/search")
def search_cards(query: str, page: int = Query(1, ge=1)):
    try:
        response = requests.get(SCRYFALL_URL, params={"q": query, "page": page})
        response.raise_for_status()
        data = response.json()

        if "data" in data:
            return {
                "cards": data["data"],
                "has_more": data.get("has_more", False),
                "next_page": page + 1 if data.get("has_more", False) else None
            }
        else:
            return {"error": "Unexpected response structure from Scryfall."}

    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred while fetching data: {str(e)}"}
