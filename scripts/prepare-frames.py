"""Optimize real renders; recover verified WebP frames when raw caches are absent."""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument("--require-complete",action="store_true")
args=parser.parse_args()
spec=json.loads((root/"config/journey.json").read_text())
current_source=hashlib.sha256((root/"scripts/build-scene.py").read_bytes()+(root/"config/journey.json").read_bytes()+(root/"scripts/make-screens.py").read_bytes()).hexdigest()
raw=root/"public/journey/raw"; dest=root/"public/journey/frames"
dest.mkdir(parents=True,exist_ok=True)
manifest_path=root/"config/render-manifest.json"
entries={}; reused=0
previous=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
if previous.get("sourceSha256")==current_source:
    for frame in previous.get("frames",[]):
        path=root/"public"/frame["src"].lstrip("/")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=frame["sha256"]:
            raise SystemExit("Stored frame integrity mismatch: "+str(path))
        with Image.open(path) as image: size=image.size
        entries[frame["src"]]=(frame,size,current_source); reused+=1
for metadata in sorted(raw.glob("frame-*.json")):
    details=json.loads(metadata.read_text()); image_path=root/details["file"]
    if not image_path.is_file(): continue
    name=metadata.stem+".webp"; target=dest/name
    with Image.open(image_path) as image:
        size=image.size
        image.convert("RGB").save(target,"WEBP",quality=86,method=5)
    frame={"src":"/journey/frames/"+name,"progress":details["progress"],"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"samples":details["samples"]}
    entries[frame["src"]]=(frame,size,details["sourceSha256"])
frames=[entry[0] for _,entry in sorted(entries.items())]
sizes={entry[1] for entry in entries.values()}; source_hashes={entry[2] for entry in entries.values()}
if any(w<640 or h<400 for w,h in sizes): raise SystemExit("Render resolution below the presentation budget.")
complete=len(frames)==spec["frameCount"] and source_hashes=={current_source} and len(sizes)==1 and all(abs(frame["progress"]-i/(spec["frameCount"]-1))<1e-9 for i,frame in enumerate(frames))
if args.require_complete and not complete: raise SystemExit(f"Refusing release manifest: only {len(frames)}/{spec['frameCount']} current, consistent frames.")
poster=raw/"poster.png"
if not poster.is_file() and frames and not (root/"public/journey/poster.webp").is_file(): poster=raw/"frame-000.png"
if poster.is_file():
    with Image.open(poster) as image: image.convert("RGB").save(root/"public/journey/poster.webp","WEBP",quality=93,method=6)
width,height=next(iter(sizes),(960,640))
total=sum((root/"public"/frame["src"].lstrip("/")).stat().st_size for frame in frames)
manifest={"complete":complete,"frames":frames,"poster":"/journey/poster.webp","width":width,"height":height,"sourceSha256":next(iter(source_hashes)) if len(source_hashes)==1 else None,"totalFrameBytes":total}
manifest_path.write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"frames":len(frames),"complete":complete,"frameBytes":total,"verifiedExistingFrames":reused}))
