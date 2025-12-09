import string
from itertools import product

def fnv1_hash(s):
    h = 2166136261
    for c in s.lower().encode('ascii'):
        h = ((h * 16777619) ^ c) & 0xFFFFFFFF
    return h

targets = {0x787E716E, 0x12ADE91F, 0x10D83379, 0x49B37C07}

# Load dictionary
with open('wwiseRE/lotr_dictionary.txt', 'r') as f:
    words = set(w.strip().lower() for w in f if w.strip() and 2 <= len(w.strip()) <= 15)

print(f'Loaded {len(words)} dictionary words')

# Try word_word combinations
print('\nTesting word_word combinations...')
found = {}

for w1 in words:
    if len(w1) > 10:
        continue
    for w2 in words:
        if len(w2) > 10:
            continue
        test = f'{w1}_{w2}'
        h = fnv1_hash(test)
        if h in targets:
            found[h] = test
            print(f'  FOUND: 0x{h:08X} = {test}')

print(f'\nFound {len(found)}/4 targets with word_word')
for h, name in sorted(found.items()):
    print(f'  0x{h:08X} = {name}')

