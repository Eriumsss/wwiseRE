#!/usr/bin/env python3
"""
Scan decompiled C files for hardcoded Wwise event IDs.
Cross-references against extracted_events.json to identify known events.
Focus on audio-related functions and filter out common non-event patterns.
"""

import os
import re
import json
from pathlib import Path

# Paths
DECOMPILED_DIR = Path("Conquest/decompiled")
EVENTS_JSON = Path("wwiseRE/extracted_events.json")
OUTPUT_FILE = Path("wwiseRE/hardcoded_events_found.txt")

# Audio-related function addresses (known PostEvent wrappers and callers)
AUDIO_FUNCTIONS = {
    '00855712', '0085567a', '00855826', '008ed372', '00560f90', '00561360',
    '00855c0', '0085562d4', '0084afbf', '008477af', '00910620', '007ff940',
    '007136c8', '00817b83'
}

# Exclude common non-event hex patterns (bitmasks, floats, CRC, addresses)
EXCLUDE_PATTERNS = {
    # Common bitmasks
    '0x3fffffff', '0x7fffffff', '0xffffffff', '0x80000000', '0x40000000',
    '0x20000000', '0x10000000', '0xc0000000', '0xe0000000', '0xf0000000',
    '0xbfffffff', '0x0fffffff',
    # IEEE 754 floats (1.0f, -1.0f, 0.5f, etc.)
    '0x3f800000', '0xbf800000', '0x3f000000', '0x40000000', '0x41200000',
    # CRC/hash constants
    '0xedb88320', '0x7efefeff', '0x81010100',
    # FourCC/magic numbers
    '0x61636374',  # 'acct'
}

def load_known_events():
    """Load all known event IDs from extracted_events.json"""
    with open(EVENTS_JSON, 'r') as f:
        data = json.load(f)

    # Convert to set of hex strings (lowercase) for fast lookup
    known = {}
    for event_id, info in data.get('events', {}).items():
        hex_id = f"0x{int(event_id):08x}"
        known[hex_id.lower()] = {
            'decimal': event_id,
            'bank': info.get('bank', 'Unknown'),
            'name': info.get('name')
        }
    return known

def find_hex_constants(file_path, check_audio_context=True):
    """Find all 8-digit hex constants in a C file"""
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return results

    # Check if file references audio functions
    is_audio_related = False
    if check_audio_context:
        for func in AUDIO_FUNCTIONS:
            if func.lower() in content.lower():
                is_audio_related = True
                break

    # Pattern for 32-bit hex constants (0x followed by 8 hex digits)
    pattern = re.compile(r'\b0x([0-9a-fA-F]{8})\b')

    for line_num, line in enumerate(lines, 1):
        for match in pattern.finditer(line):
            hex_val = match.group(0).lower()

            # Skip known non-event patterns
            if hex_val in EXCLUDE_PATTERNS:
                continue

            # Skip likely memory addresses (start with 00, 7f, etc.)
            first_byte = hex_val[2:4]
            if first_byte in ('00', '7f', 'ff', '01'):
                continue

            results.append({
                'file': file_path.name,
                'line': line_num,
                'hex': hex_val,
                'context': line.strip()[:100],
                'audio_related': is_audio_related
            })
    return results

def main():
    print("Loading known events from extracted_events.json...")
    known_events = load_known_events()
    print(f"  Loaded {len(known_events)} known event IDs")

    print(f"\nScanning {DECOMPILED_DIR} for hardcoded hex constants...")

    matched_events = {}
    unmatched_hex = {}
    audio_related_hex = {}  # Hex values in audio-related files

    c_files = list(DECOMPILED_DIR.glob("*.c"))
    print(f"  Found {len(c_files)} .c files to scan")

    for i, cfile in enumerate(c_files):
        if i % 500 == 0:
            print(f"  Processing file {i}/{len(c_files)}...")

        findings = find_hex_constants(cfile)
        for f in findings:
            hex_val = f['hex']
            if hex_val in known_events:
                if hex_val not in matched_events:
                    matched_events[hex_val] = {
                        'info': known_events[hex_val],
                        'occurrences': []
                    }
                matched_events[hex_val]['occurrences'].append(f)
            else:
                # Prioritize audio-related files
                if f.get('audio_related'):
                    if hex_val not in audio_related_hex:
                        audio_related_hex[hex_val] = []
                    audio_related_hex[hex_val].append(f)
                else:
                    if hex_val not in unmatched_hex:
                        unmatched_hex[hex_val] = []
                    unmatched_hex[hex_val].append(f)

    # Write results
    print(f"\nWriting results to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as out:
        out.write("=" * 80 + "\n")
        out.write("HARDCODED WWISE EVENT IDs FOUND IN DECOMPILED CODE\n")
        out.write("=" * 80 + "\n\n")

        # Section 1: Audio-related hex values (highest priority)
        out.write(f"AUDIO-RELATED HEX VALUES (in functions referencing audio code): {len(audio_related_hex)}\n")
        out.write("-" * 80 + "\n\n")

        for hex_val, occurrences in sorted(audio_related_hex.items(), key=lambda x: -len(x[1])):
            decimal_val = int(hex_val, 16)
            out.write(f"{hex_val} (decimal: {decimal_val}) - {len(occurrences)} occurrence(s)\n")
            for occ in occurrences[:5]:
                out.write(f"    {occ['file']}:{occ['line']} - {occ['context']}\n")
            if len(occurrences) > 5:
                out.write(f"    ... and {len(occurrences) - 5} more\n")
            out.write("\n")

        # Section 2: Matched known events
        out.write("\n" + "=" * 80 + "\n")
        out.write(f"MATCHED EVENTS (found in extracted_events.json): {len(matched_events)}\n")
        out.write("-" * 80 + "\n\n")

        for hex_val, data in sorted(matched_events.items()):
            info = data['info']
            out.write(f"Event: {hex_val} (decimal: {info['decimal']})\n")
            out.write(f"  Bank: {info['bank']}\n")
            if info['name']:
                out.write(f"  Name: {info['name']}\n")
            out.write(f"  Found in {len(data['occurrences'])} location(s):\n")
            for occ in data['occurrences'][:5]:
                out.write(f"    {occ['file']}:{occ['line']} - {occ['context']}\n")
            if len(data['occurrences']) > 5:
                out.write(f"    ... and {len(data['occurrences']) - 5} more\n")
            out.write("\n")

        out.write("\n" + "=" * 80 + "\n")
        out.write(f"OTHER UNMATCHED HEX VALUES: {len(unmatched_hex)}\n")
        out.write("-" * 80 + "\n\n")

        # Only show hex values that appear multiple times
        frequent_unmatched = {k: v for k, v in unmatched_hex.items() if len(v) >= 2}
        out.write(f"Showing {len(frequent_unmatched)} values that appear 2+ times:\n\n")
        
        for hex_val, occurrences in sorted(frequent_unmatched.items(), 
                                            key=lambda x: -len(x[1])):
            out.write(f"{hex_val} - appears {len(occurrences)} time(s)\n")
            for occ in occurrences[:3]:
                out.write(f"    {occ['file']}:{occ['line']} - {occ['context']}\n")
            out.write("\n")
    
    print(f"\nDone!")
    print(f"  Matched known events: {len(matched_events)}")
    print(f"  Unmatched hex values: {len(unmatched_hex)}")
    print(f"  Results written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

