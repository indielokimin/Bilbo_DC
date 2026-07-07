import os
import random
import re
import time

import discord
from dotenv import load_dotenv

from keep_alive import keep_alive # NEW



load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

keep_alive()  # NEW



PERSONAS = [
    {
        "name": "cat",
        "triggers": [
            r"\bcats?\b",
            r"\bkitty\b",
            r"\bkitten\b",
            r"\bkitties\b",
            r"here\s+kitty\s*,?\s*kitty",
            r"\bmeow\b",
            r"\bBilbo\b",
            r"\bbilbo\b",
            r"\bpspspspsps\b",
        ],
        "cooldown_seconds": 10,
        "responses": [
            "Meow.",
            "*yawns and stretches*",
            "Mrrrp?",
            "*knocks something off the table and stares at you*",
            "purrrrr...",
            "Hiss! ...just kidding. Meow.",
            "*slow blinks at you*",
            "Meow meow!",
            "Nyaa~",
            "*ignores you completely*",
            "*rubs against your leg*",
            "Feed me.",
            "*chases a laser dot that isn't there*",
            "MEOW.",
            "*curls up and pretends you don't exist*",
            "*chews plastic*",
            "Mew! Mew! Mewww!",
            "*lays across your keyboard lazily*",
            "*hacks up hairball*",
            "*purrs aggressively*",
            "*jumps into a box*",
            "*gingerly sticks a paw in your cereal*",
            "*eyes your food*",
            "*sits on your lap*",
            "*whips tail against the floor*"
        ],
        "interactions": [
            {
                "triggers": [r"wakey\s+wakey", r"wake\s+up"],
                "response": "*bap baps you*",    
            },
            {
                "triggers": [r"good\s+kitty", r"good\s+cat", r"love\s+you\s+Bilbo"],
                "response": "*purrs and rubs against your leg*",
            },
            {
                "triggers": [r"bad\s+kitty", r"bad\s+cat", r"this\s+mf", r"fuck\s+you\s+Bilbo", r"fuck\s+you"],
                "responses": [
                    "*bites you*",
                    "*HISS*",
                    "Bitch, I own you.",
                    "*smacks you with a paw*",
                ],
            },
            {   "triggers": [r"who\s+is\s+your\s+favorite\s+human"],
                "response": "The one called Jade",
            },
            {   "triggers": [r"\btuna\b"],
                "responses": [
                    "*perks up ears*",
                    "Mrrow?",
                    "Ekekekeke",
                    "*zooms across the room*",
                ],
            },
            {   "triggers": [r"bite\s+thomas"],
                "response": "*bites Thomas on the [censored]*",
            },
        ],
    },
]


class Persona:
    def __init__(self, data: dict):
        self.name = data["name"]
        self.patterns = [re.compile(p, re.IGNORECASE) for p in data["triggers"]]
        self.responses = data["responses"]
        self.cooldown_seconds = data.get("cooldown_seconds", 5)
        self.interactions = [
            {
                "patterns": [re.compile(p, re.IGNORECASE) for p in interaction["triggers"]],
                "responses": interaction["responses"] if "responses" in interaction else [interaction["response"]],
            }
            for interaction in data.get("interactions", [])
        ]
        self._last_fired: dict[int, float] = {}  # channel_id -> timestamp

    def on_cooldown(self, channel_id: int) -> bool:
        last = self._last_fired.get(channel_id, 0)
        return (time.monotonic() - last) < self.cooldown_seconds

    def get_response(self, content: str) -> str | None:
        for interaction in self.interactions:
            if any(p.search(content) for p in interaction["patterns"]):
                return random.choice(interaction["responses"])
        if any(p.search(content) for p in self.patterns):
            return random.choice(self.responses)
        return None

    def mark_fired(self, channel_id: int) -> None:
        self._last_fired[channel_id] = time.monotonic()


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
personas = [Persona(data) for data in PERSONAS]


@client.event
async def on_ready():
    print(f"Logged in as {client.user} — loaded personas: {[p.name for p in personas]}")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    for persona in personas:
        response = persona.get_response(message.content)
        if response is not None:
            if persona.on_cooldown(message.channel.id):
                return
            persona.mark_fired(message.channel.id)
            await message.channel.send(response)
            return  # only one persona responds per message


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("DISCORD_TOKEN not set. Create a .env file with DISCORD_TOKEN=your-bot-token-here")
    client.run(TOKEN)
