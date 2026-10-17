"""Optimize genuine Blender renders and publish an exact frame manifest."""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument("--require-complete",action="store_true")
args=parser.parse_args()
spec=json.loads((root/"config/journey.json").read_text())
raw=root/"public/journey/raw"; dest=root/"public/journey/frames"
dest.mkdir(parents=True,exist_ok=True)
frames=[]; source_hashes=set(); sizes=set(); total=0
for metadata in sorted(raw.glob("frame-*.json")):
    details=json.loads(metadata.read_text()); image_path=root/details["file"]
    if not image_path.is_file(): continue
    name=metadata.stem+".webp"
    with Image.open(image_path) as image:
        width,height=image.size
        if width<640 or height<400: raise SystemExit("Render resolution below the presentation budget.")
        sizes.add((width,height))
        target=dest/name
        image.convert("RGB").save(target,"WEBP",quality=86,method=5)
    source_hashes.add(details["sourceSha256"]); total+=target.stat().st_size
    frames.append({"src":"/journey/frames/"+name,"progress":details["progress"],"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"samples":details["samples"]})
complete=len(frames)==spec["frameCount"] and len(source_hashes)==1 and len(sizes)==1 and all(abs(frame["progress"]-i/(spec["frameCount"]-1))<1e-9 for i,frame in enumerate(frames))
if args.require_complete and not complete: raise SystemExit(f"Refusing release manifest: only {len(frames)}/{spec['frameCount']} consistent frames.")
poster=raw/"poster.png"
if not poster.is_file() and frames: poster=raw/"frame-000.png"
if poster.is_file():
    with Image.open(poster) as image: image.convert("RGB").save(root/"public/journey/poster.webp","WEBP",quality=93,method=6)
manifest={"complete":complete,"frames":frames,"poster":"/journey/poster.webp","width":width if frames else 960,"height":height if frames else 640,"sourceSha256":next(iter(source_hashes),None),"totalFrameBytes":total}
(root/"config/render-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"frames":len(frames),"complete":complete,"frameBytes":total}))
