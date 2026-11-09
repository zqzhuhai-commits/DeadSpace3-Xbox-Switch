# Awakened test build on the 1.0.1 baseline

This is an experimental source change, not a console-verified release. It keeps
1.0.1's renderer and uses a separate recompiled module for Awakened. The XEX and
shader resources are supplied by the user and are not part of the source patch.

## Inputs

- The original `tu/` directory containing default.xex, default.xexp,
  deadspace_game_f.xex, deadspace_game_f.xexp.
- Awakened's **own** deadspace_game_f.xex. The supported SHA-256 is
  `53cb2646493825f3ba52c8df737b9a5bf2ddda04430d4ca1ab7404b3cb706c34`.
  This file is copied to an internal build location as awakened.xex; do not rename
  or replace files in the SD card's DLC directory.

With the normal build prerequisites installed:

```sh
DLC_XEX=/absolute/path/to/dlc/deadspace_game_f.xex JOBS=4 \
  ds3/tools/build_mac.sh /absolute/path/to/tu
```

The codegen host tool must include the pinned patches already described in
`tools/codegen.sh`; an unpatched upstream rexglue binary is not equivalent.

## Changes

- Separate codegen processes for the base and DLC (their guest images overlap),
  then a merged module registry and locally linked Awakened module with matching
  shader/audio/CPU hooks.
- Match the supported DLC's entry point when resolving its recompiled module,
  including unload; the base and DLC executables share the same filename.
- Awakened-specific setjmp/longjmp, callback and branch hints.
- Awakened's scene-size variables are at 0x890C13F8 and 0x890C13FC; the base
  game's variables stay at 0x890B1378 and 0x890B137C.
- Hook settings are defined once in the title, shared by both game modules.

## Console test

Back up the existing NRO and saves. Replace only the NRO; retain the existing
TU, disc directories, DLC resources, shader library and shader cache. Launch via
Homebrew Menu in title takeover. Check the startup version, the base campaign,
Awakened chapter 1, save/reload and the chapter-selection operation that crashed.
Keep the new logs and crash report if a failure occurs. Restoring the backed-up
NRO rolls back the program; retain the save backup separately.
