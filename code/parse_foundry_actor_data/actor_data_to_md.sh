#!/bin/bash

# Target the directory containing your actors
ACTOR_DIR="../../ai_data/foundry/actors/raw_data"

# Loop recursively through all .json files in the actors directory
find "$ACTOR_DIR" -type f -name "*.json" | while read -r file; do

  # SKIP if the file is already a simplified file
  if [[ "$file" == *"_simple.md"* || "$file" == *"_simple.json"* ]]; then
    continue
  fi

  # Define the output file path as .md
  output_file="${file%.json}_simple.md"

  echo "Processing: $file -> $output_file"

  # Run jq to format the data into a Markdown template
  jq -r '
    "# \(.name)\n" +
    "**Race:** \(.system.details.race // "Unknown") | **Class:** \((.items[]? | select(.type == "class") | .name) // "Unknown")\n" +
    "**Level:** \(.system.details.level // "N/A") | **Alignment:** \(.system.details.alignment // "Unaligned")\n\n" +
    
    "## Physical Description\n" +
    "- **Age:** \(.system.details.age // "N/A")\n" +
    "- **Height/Weight:** \(.system.details.height // "N/A") / \(.system.details.weight // "N/A")\n" +
    "- **Appearance:** \(.system.details.appearance // "No description provided.")\n\n" +
    
    "## Statistics\n" +
    "| STR | DEX | CON | INT | WIS | CHA |\n" +
    "|-----|-----|-----|-----|-----|-----|\n" +
    "| \(.system.abilities.str.value) | \(.system.abilities.dex.value) | \(.system.abilities.con.value) | \(.system.abilities.int.value) | \(.system.abilities.wis.value) | \(.system.abilities.cha.value) |\n" +
    "- **HP:** \(.system.attributes.hp.value)/\(.system.attributes.hp.max)\n" +
    "- **AC:** \(.system.attributes.ac.value // "N/A")\n" +
    "- **Languages:** \(.system.traits.languages.value | join(", "))\n" +
    "- **Movement:** \(.system.attributes.movement.walk) \(.system.attributes.movement.units)\n\n" +
    
    "## Personality & Lore\n" +
    "- **Trait:** \(.system.details.trait // "N/A")\n" +
    "- **Ideal:** \(.system.details.ideal // "N/A")\n" +
    "- **Bond:** \(.system.details.bond // "N/A")\n" +
    "- **Flaw:** \(.system.details.flaw // "N/A")\n\n" +
    
    "## Biography\n" +
    ((.system.details.biography.value // "") | gsub("<[^>]*>"; "") | gsub("&nbsp;"; " ") | gsub("\n"; " "))
  ' "$file" > "$output_file"

done

echo "All characters converted to Markdown lore sheets!"