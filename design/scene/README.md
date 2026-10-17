# Editable original property

`IP-NET-Property.blend` contains the authored building, devices, materials,
lighting and a saved exterior camera pose. It opens in Blender 4.3+ and its
used display textures are packed into the file.

The deterministic source of the full moving journey is
`scripts/build-scene.py` with `config/journey.json`. Camera motion and system
states are evaluated in that script; the saved file is an inspectable scene,
not a separately keyframed finished animation. Rebuild from the script to
reproduce the frame sequence and additional intercom display states.

This is a fictional illustrative property, not a client project.
