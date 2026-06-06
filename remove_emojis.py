import re
import os

filepath = r"c:\Users\meghanar\Downloads\boc-analytics\app.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the emojis to remove
emojis_to_remove = [
    '🏠', '📈', '💰', '🏪', '📉', '🔮', '🚨', '👤', '🌍', '📅', '💱', '🏷️', '🔍', 
    '🚀', '💡', '🏆', '📌', '⚠️', '✅', '🔴', '🗳️', '🔧', '⛓️', '📊', '📉'
]

# Remove emojis with optional following space
for emoji in emojis_to_remove:
    content = content.replace(f"{emoji} ", "")
    content = content.replace(emoji, "")

# Some headers might have been like "## 🏠 Executive Dashboard" -> "## Executive Dashboard"
# Let's fix any double spaces created
content = re.sub(r' +', ' ', content)

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Removed emojis successfully!")
