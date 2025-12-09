#!/usr/bin/env python3
"""
Extract Event IDs from organized BNK XML files.

Parses the Organized_Final_AllLanguages directory structure to extract:
- Bank name (from folder structure)
- Event IDs (from CAkEvent objects in XML)
- TXTP filenames (for initial event names)

Outputs:
- extracted_events.json: Complete mapping of event ID -> bank name
- Updates for hash_dictionary.cpp

Usage: python extract_events_from_xml.py
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Configuration
ORGANIZED_DIR = Path(__file__).parent / "Organized_Final_AllLanguages"
ROOT_DIR = ORGANIZED_DIR / "root"
ENGLISH_DIR = ORGANIZED_DIR / "Languages" / "english_us_"
OUTPUT_JSON = Path(__file__).parent / "extracted_events.json"

# Regex to extract event ID from XML CAkEvent entries
# Pattern: <object name="CAkEvent" index="XX">...<field ... name="ulID" value="NNNN"/>
EVENT_ID_PATTERN = re.compile(
    r'<object\s+name="CAkEvent"[^>]*>.*?'
    r'<field[^>]+name="ulID"\s+value="(\d+)"',
    re.DOTALL
)

# Simpler line-by-line pattern for ulID in CAkEvent context
ULID_LINE_PATTERN = re.compile(r'name="ulID"\s+value="(\d+)"')


def extract_events_from_xml(xml_path: Path) -> List[int]:
    """Extract all CAkEvent IDs from a BNK XML file."""
    event_ids = []
    try:
        with open(xml_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find all CAkEvent blocks and extract their ulID values
        in_event = False
        for line in content.split('\n'):
            if 'name="CAkEvent"' in line:
                in_event = True
            elif in_event and 'name="ulID"' in line:
                match = ULID_LINE_PATTERN.search(line)
                if match:
                    event_ids.append(int(match.group(1)))
                in_event = False
            elif in_event and '</object>' in line:
                in_event = False
                
    except Exception as e:
        print(f"  Error parsing {xml_path.name}: {e}")
    
    return event_ids


def extract_txtp_names(bank_dir: Path) -> Dict[int, str]:
    """Extract event ID -> name mapping from TXTP filenames."""
    txtp_map = {}
    for txtp_file in bank_dir.glob("*.txtp"):
        # Parse TXTP filename: BankName-NNNN-event*.txtp
        # e.g., "HeroSauron-0075-event.txtp" or "BaseCombat-0709-event [xxx=yyy].txtp"
        name = txtp_file.stem
        # Remove switch parameters like [123=456]
        name = re.sub(r'\s*\[[^\]]+\]', '', name)
        # Remove {r} {l=en} markers
        name = re.sub(r'\s*\{[^}]+\}', '', name)
        name = name.strip()
        
        # The TXTP name becomes the event name for display
        txtp_map[name] = txtp_file.name
    
    return txtp_map


def scan_bank_folder(bank_path: Path, bank_name: str) -> Dict[int, dict]:
    """Scan a bank folder for XML and TXTP files."""
    events = {}
    
    # Find the XML file (named like NNNNNN.bnk.xml)
    for xml_file in bank_path.glob("*.bnk.xml"):
        event_ids = extract_events_from_xml(xml_file)
        print(f"  {bank_name}: {len(event_ids)} events from {xml_file.name}")
        
        for eid in event_ids:
            events[eid] = {
                'bank': bank_name,
                'bank_id': xml_file.stem.replace('.bnk', ''),
                'name': None,  # Will be filled from TXTP
                'source': 'xml'
            }
    
    # Match TXTP names to events
    txtp_names = extract_txtp_names(bank_path)
    # TXTPs have format BankName-NNNN-event, where NNNN is object index
    # We need the actual event ID from the XML
    
    return events


def scan_directory(base_dir: Path, label: str) -> Dict[int, dict]:
    """Scan a directory structure (root or language folder)."""
    all_events = {}
    
    print(f"\n[{label}]")
    
    if not base_dir.exists():
        print(f"  Directory not found: {base_dir}")
        return all_events
    
    for bank_folder in sorted(base_dir.iterdir()):
        if not bank_folder.is_dir():
            continue
        
        bank_name = bank_folder.name
        
        # Each bank folder contains a subfolder with the bank ID
        for id_folder in bank_folder.iterdir():
            if id_folder.is_dir():
                events = scan_bank_folder(id_folder, bank_name)
                all_events.update(events)
    
    return all_events


def main():
    print("=" * 70)
    print("Extract Events from Organized BNK XMLs")
    print("=" * 70)
    
    all_events = {}
    
    # Scan root (SFX banks)
    root_events = scan_directory(ROOT_DIR, "ROOT (SFX)")
    all_events.update(root_events)
    
    # Scan english_us_ (voice banks)
    english_events = scan_directory(ENGLISH_DIR, "ENGLISH_US (Voice)")
    all_events.update(english_events)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"[SUMMARY]")
    print(f"  Total events extracted: {len(all_events)}")
    
    # Count by bank
    by_bank = defaultdict(int)
    for eid, info in all_events.items():
        by_bank[info['bank']] += 1
    
    print(f"  Banks with events: {len(by_bank)}")
    print("\n  Events per bank:")
    for bank, count in sorted(by_bank.items(), key=lambda x: -x[1])[:20]:
        print(f"    {bank}: {count}")
    
    # Save to JSON
    output = {
        'total_events': len(all_events),
        'banks': dict(by_bank),
        'events': {str(k): v for k, v in all_events.items()}
    }
    
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n[OUTPUT] Saved to: {OUTPUT_JSON}")


if __name__ == '__main__':
    main()

