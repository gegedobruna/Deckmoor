from fastapi import FastAPI, Query
import requests
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:8080",
    "https://gegedobruna.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
SCRYFALL_URL = "https://api.scryfall.com/cards/search"
SCRYFALL_SETS_URL = "https://api.scryfall.com/sets"


@app.get("/")
def read_root():
    return {"message": "Welcome to the MTG Deckbuilder API! Use /search to search for cards."}


@app.get("/sets")
async def get_sets():
    """Fetch all Magic: The Gathering sets from Scryfall API."""
    try:
        response = requests.get(SCRYFALL_SETS_URL)
        response.raise_for_status()
        data = response.json()

        if "data" in data:
            sets = [{"code": set_data.get("code"), "name": set_data.get("name")}
                    for set_data in data.get("data", [])]
            return {"sets": sets}
        else:
            return {"error": "Unexpected response structure from Scryfall."}

    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred while fetching sets: {str(e)}"}


@app.get("/search")
async def search_cards(
        query: str = "",
        page: int = Query(1, ge=1),
        # Filter parameters
        mana_min: int = Query(0, ge=0),
        mana_max: int = Query(16, le=20),
        colors: Optional[str] = None,
        types: Optional[str] = None,
        supertypes: Optional[str] = None,
        subtype: Optional[str] = None,
        rarities: Optional[str] = None,
        sets: Optional[str] = None,
        power_value: Optional[int] = None,
        power_operator: Optional[str] = None,
        toughness_value: Optional[int] = None,
        toughness_operator: Optional[str] = None
):
    """
    Search for Magic: The Gathering cards with various filters.
    Returns only 15 cards per page for pagination.
    """
    try:
        # Parse filter parameters
        color_list = colors.split(',') if colors else []
        type_list = types.split(',') if types else []
        supertype_list = supertypes.split(',') if supertypes else []
        rarity_list = rarities.split(',') if rarities else []
        set_list = sets.split(',') if sets else []

        # Build Scryfall query parts
        scryfall_query_parts = []

        # Add text query if exists
        if query.strip():
            scryfall_query_parts.append(query.strip())

        # Add mana cost filter
        if mana_min > 0 or mana_max < 16:
            scryfall_query_parts.append(f"cmc>={mana_min} cmc<={mana_max}")

        # Add color filter
        if color_list:
            color_query = "c:" + "".join(color_list)
            scryfall_query_parts.append(color_query)

        # Add type filter (AND logic)
        for type_name in type_list:
            scryfall_query_parts.append(f"t:{type_name}")

        # Add supertype filter
        for supertype in supertype_list:
            scryfall_query_parts.append(f"t:{supertype}")

        # Add subtype filter
        if subtype:
            scryfall_query_parts.append(f"st:{subtype}")

        # Add rarity filter (OR logic)
        if rarity_list:
            rarity_query = " OR ".join([f"r:{rarity}" for rarity in rarity_list])
            scryfall_query_parts.append(f"({rarity_query})")

        # Add set filter
        for set_code in set_list:
            scryfall_query_parts.append(f"s:{set_code}")

        # Add power filter
        if power_value is not None and power_operator:
            operator_map = {"equal": "=", "greater": ">", "less": "<"}
            op = operator_map.get(power_operator, "=")
            scryfall_query_parts.append(f"pow{op}{power_value}")

        # Add toughness filter
        if toughness_value is not None and toughness_operator:
            operator_map = {"equal": "=", "greater": ">", "less": "<"}
            op = operator_map.get(toughness_operator, "=")
            scryfall_query_parts.append(f"tou{op}{toughness_value}")

        # Combine all query parts
        scryfall_query = " ".join(scryfall_query_parts)

        # Default search if no query/filters
        if not scryfall_query:
            scryfall_query = "type:creature"

        # Pagination setup
        cards_per_page = 16
        scryfall_page = ((page - 1) * cards_per_page) // 175 + 1

        # Make API request
        response = requests.get(
            SCRYFALL_URL,
            params={"q": scryfall_query, "page": scryfall_page}
        )
        response.raise_for_status()
        data = response.json()

        if "data" in data:
            all_cards = data["data"]
            total_cards = data.get("total_cards", 0)
            offset = ((page - 1) * cards_per_page) % 175
            paginated_cards = all_cards[offset:offset + cards_per_page]

            # Handle cases where we need the next page
            if not paginated_cards and data.get("has_more", False):
                next_response = requests.get(
                    SCRYFALL_URL,
                    params={"q": scryfall_query, "page": scryfall_page + 1}
                )
                next_response.raise_for_status()
                next_data = next_response.json()
                if "data" in next_data:
                    paginated_cards = next_data["data"][:cards_per_page]

            has_more = (page * cards_per_page) < total_cards

            return {
                "cards": paginated_cards,
                "has_more": has_more,
                "next_page": page + 1 if has_more else None,
                "total_cards": total_cards,
                "applied_query": scryfall_query
            }
        else:
            return {"error": "Unexpected response structure from Scryfall."}

    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred while fetching data: {str(e)}"}