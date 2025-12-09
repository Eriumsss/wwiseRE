#!/usr/bin/env python3
"""
Build comprehensive Wwise event name dictionary from all game data sources.
Tests generated names against known event IDs using FNV-1a hash.
"""

import os
import re
import json

# FNV-1 hash (Wwise uses FNV-1, not FNV-1a, with lowercase)
# FNV-1: multiply first, then XOR
# FNV-1a: XOR first, then multiply
def wwise_hash(s):
    h = 2166136261
    for c in s.lower():
        h = (h * 16777619) & 0xFFFFFFFF
        h ^= ord(c)
    return h

# Load known event IDs from extracted_events.json
def load_known_events():
    known_ids = {}
    with open('extracted_events.json', 'r') as f:
        data = json.load(f)
    # Structure: {"events": {"event_id": {"bank": "...", ...}}}
    for event_id, info in data.get('events', {}).items():
        known_ids[int(event_id)] = info.get('bank', 'Unknown')
    return known_ids

# Source 1: Binary strings.txt
def extract_from_strings():
    candidates = set()
    with open('../Conquest/analysis/strings.txt', 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if ':' in line:
                text = line.split(':', 1)[1].strip()
                # Filter for potential event names
                if re.match(r'^[a-zA-Z][a-zA-Z0-9_]{3,50}$', text):
                    lower = text.lower()
                    if any(kw in lower for kw in ['sound', 'music', 'sfx', 'voice', 'play', 'stop', 
                                                   'event', 'attack', 'ability', 'death', 'spawn',
                                                   'footstep', 'ambient', 'hit', 'impact', 'swing',
                                                   'creature', 'hero', 'chatter', 'taunt', 'idle',
                                                   'breaker', 'capture', 'fire', 'trigger']):
                        candidates.add(text)
    return candidates

# Source 2: English.json ability names
def extract_from_english_json():
    candidates = set()
    with open('../LUA/shell/sub_blocks2/English.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for key, value in data.items():
        if 'Description' in key and 'Special Abilities' in str(value):
            parts = str(value).split('Special Abilities:')
            if len(parts) > 1:
                for line in parts[1].split('\\n'):
                    name = line.strip()
                    if name and len(name) > 2:
                        # Convert to potential event name format
                        event_name = name.lower().replace(' ', '_').replace("'", "").replace('!', '')
                        candidates.add(event_name)
                        candidates.add(f"play_{event_name}")
                        candidates.add(f"ability_{event_name}")
    return candidates

# Source 3: Hero/Unit names
def generate_hero_combinations():
    candidates = set()
    heroes = ['sauron', 'aragorn', 'gandalf', 'legolas', 'gimli', 'frodo', 'saruman',
              'witchking', 'nazgul', 'gothmog', 'lurtz', 'mouth', 'eowyn',
              'faramir', 'theoden', 'elrond', 'isildur', 'boromir', 'arwen', 'treebeard',
              'balrog', 'wormtongue', 'witch_king', 'mouth_of_sauron']

    actions = ['attack', 'swing', 'ability', 'special', 'death', 'spawn', 'taunt',
               'hit', 'impact', 'block', 'dodge', 'run', 'walk', 'idle', 'vocal',
               'charge', 'fire', 'throw', 'cast', 'heal', 'buff', 'intro', 'outro',
               'ability_1', 'ability_2', 'ability_3', 'special_1', 'special_2', 'special_3']

    suffixes = ['', '_1', '_2', '_3', '_loop', '_start', '_end', '_lp']
    prefixes = ['', 'play_', 'stop_']

    for hero in heroes:
        for action in actions:
            for prefix in prefixes:
                for suffix in suffixes:
                    candidates.add(f"{prefix}{hero}_{action}{suffix}")
        # Also add hero_intro, hero_death patterns
        candidates.add(f"{hero}_intro")
        candidates.add(f"{hero}_outro")
        candidates.add(f"play_{hero}")
        candidates.add(f"stop_{hero}")
    return candidates

# Source 4: Known event patterns from capture
def generate_known_patterns():
    candidates = set()
    base_events = [
        'swing', 'ability', 'impact', 'impact_kill', 'block', 'footstep',
        'creature_death', 'attack_vocal', 'taunt', 'cp_idle', 'cp_transition',
        'ranged_attack_charge', 'ranged_attack_release', 'stop_ability',
        'stop_music', 'stop_all_but_music', 'pause_game', 'unpause_game',
        'ui_advance', 'ui_scroll', 'ui_confirm', 'ui_cancel', 'ui_previous',
        'front_end', 'shell_amb', 'mp_good', 'mp_evil', 'training',
        'fire_sword', 'cp_capture', 'melee_attack', 'ranged_attack',
        'death', 'spawn', 'hit', 'vocal', 'charge', 'fire', 'throw',
        'cast', 'heal', 'buff', 'intro', 'outro', 'victory', 'defeat',
        'battle', 'combat', 'idle', 'walk', 'run', 'jump', 'land',
        'dodge', 'roll', 'parry', 'counter', 'combo', 'finisher',
        # New from testing
        'impact_stone', 'impact_metal', 'impact_wood', 'impact_flesh',
        'Set_State_normal', 'Set_State_character_select',
        'set_state_normal', 'set_state_character_select',
        'play_music', 'stop_sfx', 'play_sfx', 'Block',
        'ability_1', 'ability_2', 'ability_3',
        'special_1', 'special_2', 'special_3'
    ]

    for e in base_events:
        candidates.add(e)
        candidates.add(f"play_{e}")
        candidates.add(f"stop_{e}")

    return candidates

# Source 4b: Creature/SFX patterns
def generate_creature_patterns():
    candidates = set()
    creatures = ['troll', 'ent', 'oliphant', 'eagle', 'warg', 'fellbeast',
                 'balrog', 'orc', 'uruk', 'gondor', 'rohan', 'elf', 'hobbit',
                 'mumakil', 'nazgul', 'ringwraith', 'spider', 'shelob']

    sfx_objects = ['catapult', 'ballista', 'siege_tower', 'battering_ram',
                   'horse', 'trebuchet', 'ladder', 'gate', 'door', 'bridge']

    actions = ['attack', 'swing', 'death', 'spawn', 'hit', 'vocal', 'taunt',
               'roar', 'stomp', 'charge', 'fire', 'impact', 'idle', 'walk', 'run']

    for creature in creatures + sfx_objects:
        for action in actions:
            candidates.add(f"{creature}_{action}")
            candidates.add(f"play_{creature}_{action}")
            candidates.add(f"stop_{creature}_{action}")

    return candidates

# Source 5: Level-specific patterns
def generate_level_patterns():
    candidates = set()
    levels = ['helms_deep', 'helmsdeep', 'moria', 'osgiliath', 'minas_tirith', 'minastir',
              'pelennor', 'black_gates', 'blackgates', 'isengard', 'rivendell', 'shire',
              'weathertop', 'mount_doom', 'mountdoom', 'minas_morg', 'minasmorg', 'trng',
              'training', 'cori']

    suffixes = ['_amb', '_music', '_battle', '_victory', '_defeat', '_intro', '_outro',
                '_start', '_end', '_loop']

    for level in levels:
        for suffix in suffixes:
            candidates.add(f"{level}{suffix}")
            candidates.add(f"play_{level}{suffix}")
            candidates.add(f"stop_{level}{suffix}")
        candidates.add(f"{level}_intro")
        candidates.add(f"play_{level}")
        candidates.add(f"stop_{level}")

    return candidates

# Source 6: Voiceover patterns
def generate_vo_patterns():
    candidates = set()
    characters = ['aragorn', 'gandalf', 'legolas', 'gimli', 'frodo', 'sauron', 'saruman',
                  'theoden', 'eowyn', 'faramir', 'elrond', 'isildur', 'boromir', 'arwen',
                  'witchking', 'nazgul', 'gothmog', 'lurtz', 'mouth', 'wormtongue', 'treebeard',
                  'balrog', 'orc', 'uruk', 'gondor', 'rohan', 'elf', 'hobbit', 'evil_human']

    actions = ['taunt', 'death', 'spawn', 'attack', 'hit', 'victory', 'defeat',
               'objective', 'ally', 'enemy', 'help', 'follow', 'retreat', 'charge']

    for char in characters:
        for action in actions:
            candidates.add(f"{char}_{action}")
            candidates.add(f"vo_{char}_{action}")
            candidates.add(f"play_{char}_{action}")
            candidates.add(f"stop_{char}_{action}")

    return candidates

# Source 7: Additional patterns from matches
def generate_additional_patterns():
    candidates = set()

    # Level-specific patterns (based on working matches)
    levels = ['moria', 'osgiliath', 'pelennor', 'helmsdeep', 'minastir', 'minasmorg',
              'weathertop', 'isengard', 'rivendell', 'shire', 'blackgates', 'mountdoom']

    for level in levels:
        candidates.add(f"{level}_intro")
        candidates.add(f"{level}_outro")
        candidates.add(f"{level}_battle")
        candidates.add(f"{level}_victory")
        candidates.add(f"{level}_defeat")
        candidates.add(f"play_{level}")
        candidates.add(f"stop_{level}")

    # More SFX patterns
    sfx = ['oliphant', 'fellbeast', 'siege_tower', 'battering_ram', 'eagle',
           'mumakil', 'nazgul', 'catapult', 'ballista', 'horse', 'warg', 'spider']
    actions = ['attack', 'death', 'hit', 'spawn', 'vocal', 'roar', 'charge',
               'fire', 'impact', 'idle', 'move', 'stomp', 'swing', 'taunt', 'intro']

    for s in sfx:
        for a in actions:
            candidates.add(f"{s}_{a}")
            candidates.add(f"play_{s}_{a}")
            candidates.add(f"stop_{s}_{a}")

    # More hero patterns based on matches
    heroes = ['sauron', 'aragorn', 'gandalf', 'legolas', 'gimli', 'frodo', 'saruman',
              'witchking', 'nazgul', 'gothmog', 'lurtz', 'eowyn', 'faramir', 'theoden',
              'elrond', 'isildur', 'boromir', 'arwen', 'treebeard', 'wormtongue', 'mouth']
    actions = ['spawn', 'death', 'charge', 'fire', 'intro', 'outro', 'attack', 'hit',
               'ability', 'special', 'taunt', 'victory', 'defeat']

    for h in heroes:
        for a in actions:
            candidates.add(f"{h}_{a}")
            candidates.add(f"play_{h}_{a}")
            candidates.add(f"stop_{h}_{a}")

    return candidates

def main():
    print("Building Wwise event name dictionary...")
    print("=" * 60)
    
    # Load known event IDs
    known_ids = load_known_events()
    print(f"Loaded {len(known_ids)} known event IDs")
    
    # Collect candidates from all sources
    all_candidates = set()
    
    print("\nSource 1: Binary strings...")
    strings_candidates = extract_from_strings()
    print(f"  Found {len(strings_candidates)} candidates")
    all_candidates.update(strings_candidates)
    
    print("\nSource 2: English.json abilities...")
    ability_candidates = extract_from_english_json()
    print(f"  Found {len(ability_candidates)} candidates")
    all_candidates.update(ability_candidates)
    
    print("\nSource 3: Hero combinations...")
    hero_candidates = generate_hero_combinations()
    print(f"  Generated {len(hero_candidates)} candidates")
    all_candidates.update(hero_candidates)
    
    print("\nSource 4: Known event patterns...")
    pattern_candidates = generate_known_patterns()
    print(f"  Generated {len(pattern_candidates)} candidates")
    all_candidates.update(pattern_candidates)

    print("\nSource 4b: Creature/SFX patterns...")
    creature_candidates = generate_creature_patterns()
    print(f"  Generated {len(creature_candidates)} candidates")
    all_candidates.update(creature_candidates)

    print("\nSource 5: Level patterns...")
    level_candidates = generate_level_patterns()
    print(f"  Generated {len(level_candidates)} candidates")
    all_candidates.update(level_candidates)

    print("\nSource 6: Voiceover patterns...")
    vo_candidates = generate_vo_patterns()
    print(f"  Generated {len(vo_candidates)} candidates")
    all_candidates.update(vo_candidates)

    print("\nSource 7: Additional patterns...")
    additional_candidates = generate_additional_patterns()
    print(f"  Generated {len(additional_candidates)} candidates")
    all_candidates.update(additional_candidates)

    print(f"\nTotal unique candidates: {len(all_candidates)}")
    print("=" * 60)
    
    # Test all candidates against known IDs
    matches = []
    for name in all_candidates:
        h = wwise_hash(name)
        if h in known_ids:
            matches.append((name, h, known_ids[h]))
    
    print(f"\n*** MATCHES FOUND: {len(matches)} ***\n")
    
    # Sort by bank name
    matches.sort(key=lambda x: (x[2], x[0]))
    
    for name, h, bank in matches:
        print(f"  0x{h:08X} -> {name:40} [{bank}]")
    
    # Save matches to file
    with open('dictionary_matches.txt', 'w') as f:
        f.write(f"# Wwise Event Dictionary Matches\n")
        f.write(f"# Generated from game data sources\n")
        f.write(f"# Total candidates tested: {len(all_candidates)}\n")
        f.write(f"# Matches found: {len(matches)}\n\n")
        for name, h, bank in matches:
            f.write(f"0x{h:08X},{name},{bank}\n")
    
    print(f"\nResults saved to dictionary_matches.txt")

if __name__ == '__main__':
    main()

