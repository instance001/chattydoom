# Glossary (Repo Excerpt)

For the full glossary, see: https://github.com/instance001/Whatisthisgithub/blob/main/GLOSSARY.md

This file contains only the glossary entries for this repository. Mapping tag legends and global notes live in the full glossary.

## chattydoom
| Term | Alternate term(s) | Alt map | External map | Relation to existing terminology | What it is | What it is not | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ChattyDoom Barebones | ChattyDoom | ~ | ~ | Minimal VizDoom sandbox | 60-second VizDoom runner with configurable IWAD/PWAD and Python enemy brains; ships sample map placeholder and three brains | Not shipping id Software assets; not a full game mod toolkit | chattydoom/README.md |
| Enemy brain module | brain | ~ | ~ | Comparable to agent policy module | Python module exposing `decide(state) -> {action, confidence}` invoked each tick; mapped via config.yaml | Not a neural policy; not hardcoded in engine | chattydoom/README.md |
| Action adapter | action_adapter.py | = | ~ | Analogous to control mapper | Maps brain action names to VizDoom controls | Not a planner; not aware of map geometry | chattydoom/README.md |
| State adapter | state_adapter.py | = | ~ | Analogous to observation encoder | Builds state dict; uses heuristics for LOS/distance if not provided; exposes position/angle/health/armor/ammo when available | Not a full game-state mirror; may be approximate until proper hooks added | chattydoom/README.md |
| Config-driven asset map | config.yaml | = | ~ | Standard config mapping | Single config for IWAD/PWAD/music paths and enemy-class→brain bindings; includes placeholder `budgets` for future tick quotas | Not embedded defaults; not auto-downloading PWADs | chattydoom/README.md |
| Setup assets script | setup_assets.py | = | ~ | Downloader utility | Fetches Freedoom release, extracts `freedoom2.wad` into assets/iwad/, updates config paths | Not bundling IWADs by default; not handling PWAD downloads | chattydoom/README.md |
