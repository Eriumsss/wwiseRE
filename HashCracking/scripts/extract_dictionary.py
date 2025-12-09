#!/usr/bin/env python3
"""
Extract all terms from game data files and save to a static dictionary.
Run this ONCE to generate lotr_dictionary.txt
"""

import json
import re
from pathlib import Path

def extract_dictionary():
    script_dir = Path(__file__).parent
    dict_folder = script_dir / 'Dictionary canditates'
    output_file = script_dir / 'lotr_dictionary.txt'
    
    terms = set()
    
    # Patterns
    word_pattern = re.compile(r'[A-Za-z][A-Za-z0-9_]{2,24}')
    snake_pattern = re.compile(r'[a-z]{3,}')
    audio_pattern = re.compile(r'(VO|SFX|MUS|AMB|UI|FX|BGM|SE)_[A-Za-z0-9_]+', re.IGNORECASE)
    
    def is_valid_term(s: str) -> bool:
        if len(s) < 3 or len(s) > 25:
            return False
        letter_count = sum(1 for c in s if c.isalpha())
        if letter_count < len(s) * 0.7:
            return False
        if all(c in '0123456789abcdef_' for c in s):
            return False
        if len(s) >= 4 and s[0] == 'x' and all(c in '0123456789abcdef' for c in s[1:]):
            return False
        if s.startswith(('0x', '0f', 'x0', 'f0')):
            return False
        if not re.search(r'[a-z]{2}', s):
            return False
        return True
    
    def extract_from_string(s: str):
        extracted = set()
        for match in re.finditer(audio_pattern, s):
            audio_term = match.group(0).lower()
            if len(audio_term) <= 40:
                extracted.add(audio_term)
        for word in word_pattern.findall(s):
            w = word.lower()
            if is_valid_term(w):
                extracted.add(w)
            camel_parts = re.findall(r'[A-Z][a-z]+|[a-z]+', word)
            for part in camel_parts:
                p = part.lower()
                if is_valid_term(p):
                    extracted.add(p)
            for part in snake_pattern.findall(w):
                if is_valid_term(part):
                    extracted.add(part)
        return extracted
    
    # Process JSON files
    json_files = list(dict_folder.rglob('*.json'))
    print(f"Processing {len(json_files)} JSON files...")
    for i, json_path in enumerate(json_files):
        try:
            with open(json_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            terms.update(extract_from_string(content))
        except:
            pass
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(json_files)} files, {len(terms):,} terms")
    
    # Process LUA files
    lua_files = list(dict_folder.rglob('*.lua'))
    print(f"Processing {len(lua_files)} LUA files...")
    for lua_file in lua_files:
        try:
            with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            terms.update(extract_from_string(content))
        except:
            pass
    
    # Filter noise
    noise_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'has', 'his', 'how', 'its', 'may',
        'new', 'now', 'old', 'see', 'way', 'who', 'boy', 'did', 'get', 'let',
        'put', 'say', 'she', 'too', 'use', 'your', 'will', 'with', 'have',
        'this', 'that', 'from', 'they', 'been', 'call', 'come', 'each',
        'then', 'else', 'true', 'false', 'nil', 'end', 'local', 'function',
        'return', 'while', 'repeat', 'until', 'break', 'elseif',
    }
    terms -= noise_words
    
    # Sort and save
    sorted_terms = sorted(terms)
    with open(output_file, 'w', encoding='utf-8') as f:
        for term in sorted_terms:
            f.write(term + '\n')
    
    print(f"\nDone! Saved {len(sorted_terms):,} terms to {output_file}")
    print(f"Sample terms: {sorted_terms[:20]}")

if __name__ == '__main__':
    extract_dictionary()

