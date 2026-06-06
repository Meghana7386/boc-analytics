import os

filepath = r"c:\Users\meghanar\Downloads\boc-analytics\app.py"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

emojis_to_remove = [
    '🏠', '📈', '💰', '🏪', '📉', '🔮', '🚨', '👤', '🌍', '📅', '💱', '🏷️', '🔍', 
    '🚀', '💡', '🏆', '📌', '⚠️', '✅', '🔴', '🗳️', '🔧', '⛓️', '📊', '📉', '📈'
]

new_lines = []
for line in lines:
    new_line = line
    for emoji in emojis_to_remove:
        new_line = new_line.replace(f"{emoji} ", "")
        new_line = new_line.replace(emoji, "")
    new_lines.append(new_line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Removed emojis successfully without breaking indentation!")
