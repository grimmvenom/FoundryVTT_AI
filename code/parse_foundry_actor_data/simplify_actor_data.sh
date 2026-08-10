#!/bin/bash
# Summary:
# Script to simplify fields needed from Foundry VTT Actor .json files.
#

# Target the directory containing your actors
ACTOR_DIR="../../ai_data/foundry/actors/raw_data"

# Ensure the output directory exists
mkdir -p $ACTOR_DIR

# Loop recursively through all .json files in the actors directory
find "$ACTOR_DIR" -type f -name "*.json" | while read -r file; do

  # SKIP if the file is already a flattened or simple file
  if [[ "$file" == *"_simple.json"* || "$file" == *"flattened_actors.json"* ]]; then
    continue
  fi

  # Define the output file path path (e.g., Emerich.json -> Emerich_simple.json)
  output_file="${file%.json}_simple.json"

  echo "Processing: $file -> $output_file"

  # Run jq to extract data cleanly
  jq '{
    name: .name,
    class: (.items[]? | select(.type == "class") | .name),
    race: .system.details.race,
    age: .system.details.age,
    appearance: .system.details.appearance,
    biography: {
      value: (if .system.details.biography.value then (.system.details.biography.value | gsub("<[^>]*>"; "") | gsub("&nbsp;"; " ")) else "" end),
      public: (if .system.details.biography.public then (.system.details.biography.public | gsub("<[^>]*>"; "") | gsub("&nbsp;"; " ")) else "" end)
    },
    level: .system.details.level,
    height: .system.details.height,
    weight: .system.details.weight,
    skin: .system.details.skin,
    gender: .system.details.gender,
    eyes: .system.details.eyes,
    hair: .system.details.hair,
    personality: {
      alignment: .system.details.alignment,
      trait: .system.details.trait,
      ideal: .system.details.ideal,
      bond: .system.details.bond,
      flaw: .system.details.flaw
    },
    stats: {
      STR: .system.abilities.str.value,
      DEX: .system.abilities.dex.value,
      CON: .system.abilities.con.value,
      INT: .system.abilities.int.value,
      WIS: .system.abilities.wis.value,
      CHA: .system.abilities.cha.value
    },
    hp: "\(.system.attributes.hp.value)/\(.system.attributes.hp.max)",
    ac: .system.attributes.ac.value,
    languages: .system.traits.languages.value,
    movement: .system.attributes.movement
  }' "$file" > "$output_file"
done

echo "All characters processed successfully!"