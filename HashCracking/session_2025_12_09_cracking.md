# Wwise Event Hash Cracking Session - December 9, 2025 (Updated)

## Session Update - Continued Cracking Effort

### Current Status
- **Total cracked events**: 1,325 / 2,817 (47.0%)
- **Remaining events**: 1,492
- **8-char brute force**: Running at 12.4% (~208 M/s), ETA ~3.5 hours remaining

### New Events Cracked This Session
| Hash | Event Name | Bank | Method |
|------|------------|------|--------|
| 0xB53A0D23 | move_ballista | SFXBallista | 2-word combo |
| 0x783CDC38 | stop_fire_large | Ambience | 3-word combo |
| 0xD6454E24 | stop_move_ballista | SFXBallista | 3-word combo |

### Stubborn Events Analysis
The remaining 18 priority stubborn events have resisted all pattern-based attacks:
- **HeroIsildur**: 3 events (0x84405926, 0x5BBF9654, 0x2EB326D8) - no cracked events in bank for reference
- **HeroLegolas**: 2 events (0xD9A5464C, 0x214CA366) - have legolas_sa1/2/3 patterns
- **HeroGimli**: 1 event (0xFF74FDE5) - have gimli_bullskid, gimli_charge patterns
- **HeroSaruman**: 1 event (0xA6D835D7) - have saruman_fireball, saruman_staff_hit patterns
- **HeroMouth**: 1 event (0xEF688F80) - have mouth_summon pattern
- **Creatures**: 1 event (0xDD7978E6) - have creature_death, attack_vocal patterns
- **SFXSiegeTower**: 1 event (0xDCD9D5DD) - have siege_tower_* patterns
- **SFXOliphant**: 1 event (0xDF91450F) - have oli_*, oliphaunt_* patterns
- **SFXBalrog**: 1 event (0xD1E41CDA) - have balrog_* patterns (19 cracked)
- **Level_Isengard**: 1 event (0x94BDA720) - have isen_*, play_isen_* patterns
- **Ambience**: 1 event (0xE234322F) - have amb_*, stop_amb_* patterns
- **SFXBatteringRam**: 2 events (0x8DCE21D5, 0x79D92FB7) - have battering_ram_* patterns
- **SFXCatapult**: 2 events (0x0CCA70A9, 0x4C480561) - have catapult_*, crank_* patterns

### Pattern Attacks Attempted
1. **2-word combinations**: 375,769 patterns - 1 match (move_ballista)
2. **3-word combinations**: 7,515,380 patterns - 2 matches (stop_fire_large, stop_move_ballista)
3. **4-word combinations**: 460,692,794 patterns - 3 false positives (hash collisions)
4. **Targeted hero patterns**: 16,898 patterns - 0 matches
5. **Bank-specific patterns**: 15,072 patterns - 0 matches

### Brute Force Progress
- **7-char brute force**: COMPLETED - 94.9 billion patterns, 444 collisions, 0 real matches
- **8-char brute force**: RUNNING - 12.4% complete, 2,199 collisions so far, 0 real matches yet

### Recommendations
1. **Runtime capture** - Hook the game to log event names as they play (most reliable)
2. **Wait for 8-char brute force** - May find real event names in remaining 87.6%
3. **GPU acceleration** - Consider CUDA/OpenCL for 9+ char brute force
4. **Additional data sources** - Search for debug builds, other game files with strings

---

## Original Session Summary

## Overall Progress
- **Total events:** 2,817
- **Cracked:** 1,294 (45.9%)
- **Remaining:** 1,523

## This Session Results
- **Events cracked:** 25
- **Patterns tested:** ~12.9 billion
- **Hit rate:** 1 in ~516 million

### Events Cracked This Session
1. `pf_siege_tower_firepot_hit` (Level_Pelennor)
2. `helms_rain_a01` (Level_HelmsDeep)
3. `warg_trample` (SFXWarg)
4. `witchking_sa2`, `witchking_sa3` (HeroWitchKing)
5. `balrog_pickup_kill_01` (SFXBalrog)
6. `wormtongue_sa2`, `wormtongue_sa3` (HeroWormtongue)
7. `frodo_sa1`, `frodo_sa2`, `frodo_sa3` (HeroFrodo)
8. `ram_door_hit` (Level_MinasTir)
9. `gandalf_sa1`, `gandalf_sa2`, `gandalf_sa3` (HeroGandalf)
10. `water_drips_heavy_a02`, `a03`, `a04` (Level_Isengard)
11. `mouth_sa1` (HeroGandalf cross-bank)
12. `nazgul_sa3` (HeroNazgul)
13. `legolas_sa1`, `legolas_sa2`, `legolas_sa3` (HeroLegolas)
14. `yakety`, `stop_yakety` (Easter egg)

## Patterns Tested
| Attack Type | Patterns |
|-------------|----------|
| Dictionary attacks | ~4M |
| Targeted hero patterns | ~42K |
| Bank-specific patterns | ~1M |
| 5-char brute force | ~69M |
| 7-char partial brute force | ~12.8B |
| Level JSON string mining | ~25K |

## Key Discoveries
1. **`_sa` pattern** - Special ability naming (`hero_sa1`, `hero_sa2`, `hero_sa3`) universal across hero banks
2. **Consecutive hash exploitation** - Hashes differing by 1-3 = numbered variants (`_a01`, `_a02`)
3. **Level JSON mining** - Found `pf_siege_tower_firepot_hit` from game data files
4. **Cross-bank events** - Some events like `mouth_sa1` appear in unexpected banks

## Stubborn Remaining (50 priority events in 23 banks)
| Bank | Remaining | Hashes |
|------|-----------|--------|
| Creatures | 1 | 0xDD7978E6 |
| SFXSiegeTower | 1 | 0xDCD9D5DD |
| SFXOliphant | 1 | 0xDF91450F |
| SFXBalrog | 1 | 0xD1E41CDA |
| HeroSaruman | 1 | 0xA6D835D7 |
| HeroGimli | 1 | 0xFF74FDE5 |
| HeroMouth | 1 | 0xEF688F80 |
| Level_Isengard | 1 | 0x94BDA720 |
| Ambience | 2 | 0xE234322F, 0x783CDC38 |
| SFXBallista | 2 | 0xB53A0D23, 0xD6454E24 |
| SFXBatteringRam | 2 | 0x8DCE21D5, 0x79D92FB7 |
| SFXCatapult | 3 | 0x0CCA70A9, 0x90519663, 0x4C480561 |
| HeroIsildur | 3 | 0x84405926, 0x5BBF9654, 0x2EB326D8 |

## Recommendations for Next Session
1. **Runtime capture** - Hook the game to log event names as they play
2. **Additional data sources** - Search for debug builds, other game files
3. **GPU acceleration** - Use CUDA for 8+ char brute force
4. **BNK HIRC analysis** - Examine object relationships for naming clues

## Cumulative Statistics (All Sessions)
- **Total patterns tested:** ~2.3 billion (previous) + ~12.9 billion (this session) = **~15.2 billion**
- **Total events cracked:** 1,294
- **Overall hit rate:** 1 in ~11.7 million

