# Original scene and asset sources

The property and equipment are authored in `scripts/build-scene.py` using Blender
primitives, curves, procedural materials and physically based lighting. The
camera path, door motion, credential movement, intercom states, wall visibility
and locksmith hardware are evaluated from a single normalized progress value.
These models are illustrative and do not represent a manufacturer partnership
or customer installation.

`scripts/make-screens.py` creates the original fictional intercom and reception
display graphics. They contain no real customer video. There are no downloaded
stock photographs, third-party product models or generative concept images in
the rendered building film.

Cycles produces the image and auxiliary linear passes. The renderer uses a
checksum-verified Intel Open Image Denoise executable, downloaded from its
official release, to denoise the linear result before AgX display conversion.
The installation script pins both archive and executable checksums and preserves
TLS verification. OIDN is an authoring tool, not a browser dependency.

The optimized frames are derived WebP assets. `config/render-manifest.json`
records frame progress, checksums, sample count and source provenance. Raw PNGs
and intermediate EXR/PFM files are regenerable, ignored, and removed from the
static export by `scripts/clean-export.mjs`.

Local fonts are Archivo, Instrument Sans and IBM Plex Mono from their pinned
Fontsource packages. Their accompanying licenses are in `public/fonts/` and are
embedded in the self-contained review file. The custom SVG shield/lock mark is
a reconstruction for this website; an original brand vector was not supplied.

The scene is an original illustrative demonstration. It must not be relabeled
as a photographed completed client project.
