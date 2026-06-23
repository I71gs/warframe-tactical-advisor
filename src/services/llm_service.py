from __future__ import annotations
import json
import urllib.request
from typing import TYPE_CHECKING, Any
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.core.app_context import AppContext

class LLMService:
    """Offline Local LLM client integrating with local Ollama endpoints using context injection."""

    def __init__(self, context: AppContext, host: str = "http://localhost:11434") -> None:
        self.context = context
        self.host = host
        self.default_model = "gemma:2b"

    def ask(self, question: str, model_name: str | None = None) -> str:
        """Sends a contextualized query to the local Ollama LLM endpoint."""
        model = model_name or self.default_model
        prompt = self._build_contextual_prompt(question)
        
        url = f"{self.host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data.get("response", "No response content received.")
        except Exception as exc:
            logger.warning("Local LLM (Ollama) request failed: %s", exc)
            return (
                f"LLM Connection Refused: Ensure Ollama is running locally at {self.host} "
                f"with model '{model}' loaded. Fallback local rule results used."
            )

    def _build_contextual_prompt(self, question: str) -> str:
        """Injects active player state context into the LLM system prompt."""
        try:
            player = self.context.player_service.get_player()
            completed = ", ".join(player.completed_quests)
            weapons = ", ".join(player.owned_weapons)
            mods = ", ".join(player.owned_mods)
            
            context = (
                f"You are the Warframe Tactical Advisor. Answer the player's question offline.\n"
                f"Player State:\n"
                f"- Mastery Rank: {player.mastery_rank}\n"
                f"- Steel Path: {'Unlocked' if player.steel_path_unlocked else 'Locked'}\n"
                f"- Arbitrations: {'Unlocked' if player.arbitrations_unlocked else 'Locked'}\n"
                f"- Completed Quests: [{completed}]\n"
                f"- Owned Weapons: [{weapons}]\n"
                f"- Owned Mods: [{mods}]\n\n"
                f"Question: {question}\n\n"
                f"Provide a direct, concise tactical response."
            )
            return context
        except Exception:
            return f"Question: {question}"
