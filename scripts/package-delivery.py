"""Package verified static output, source, standalone review and holding page."""
from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile

root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/"config/render-manifest.json").read_text())
if not manifest["complete"]: raise SystemExit("Cannot package an incomplete film as the release.")
subprocess.run(["node","scripts/check-assets.mjs"],cwd=root,check=True)
if (root/"out/journey/raw").exists(): raise SystemExit("Raw authoring files must not be deployed.")
for frame in manifest["frames"]:
    exported=root/"out"/frame["src"].lstrip("/")
    if not exported.exists() or hashlib.sha256(exported.read_bytes()).hexdigest()!=frame["sha256"]:
        raise SystemExit("Build output is missing or stale: "+str(exported))
if not (root/"out/index.html").exists(): raise SystemExit("Build the static export first.")
status=subprocess.check_output(["git","status","--porcelain"],cwd=root,text=True)
if status.strip(): raise SystemExit("Commit source and authored assets before packaging.\n"+status)
head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
subprocess.run(["node","scripts/build-preview.mjs"],cwd=root,check=True)
dest=root/"delivery";dest.mkdir(exist_ok=True)
tracked=subprocess.check_output(["git","ls-files","-z"],cwd=root).decode().split("\0")
with zipfile.ZipFile(dest/"IP-NET-Source.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for name in filter(None,tracked):
        if Path(name).name.startswith(".env") and Path(name).name!=".env.example": raise SystemExit("Unexpected environment file in source.")
        archive.write(root/name,"ipnet-site/"+name)
with zipfile.ZipFile(dest/"IP-NET-Static-Site.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for file in sorted((root/"out").rglob("*")):
        if file.is_file(): archive.write(file,file.relative_to(root/"out"))
with zipfile.ZipFile(dest/"IP-NET-Coming-Soon.zip","w",zipfile.ZIP_DEFLATED) as archive:
    archive.write(root/"holding/index.html","index.html")
shutil.copy2(root/"preview/IP-NET-Website-Review.html",dest/"IP-NET-Website-Review.html")
(dest/"START-HERE.txt").write_text("""IP NET SECURITY & LOCKSMITH

לצפייה: הורידו את IP-NET-Website-Review.html ופתחו בדפדפן.
זהו קובץ עצמאי עם העיצוב, התמונות והאינטראקציות. אין צורך בהתקנה.

IP-NET-Static-Site.zip — קובצי האתר להעלאה לאחסון סטטי.
IP-NET-Source.zip — קוד המקור, סצנת Blender, נכסים והוראות פיתוח.
IP-NET-Coming-Soon.zip — דף זמני עצמאי עם פרטי הקשר.

האתר לא פורסם באמצעות יצירת הקבצים. הדומיין ipnetsecurity.com
מנוהל ב-Namecheap; חיבור לאחסון ול-DNS הוא שלב נפרד.

טופס הפנייה מכין הודעת אימייל או WhatsApp. המבקר בוחר ושולח
באפליקציה שלו; אין טענה שהודעה נשלחה אוטומטית דרך שרת.

"""+"Source commit: "+head+"\n",encoding="utf-8")
files=[]
for file in sorted(dest.iterdir()):
    if file.is_file() and file.name!="delivery.json":
        files.append({"file":file.name,"bytes":file.stat().st_size,"sha256":hashlib.sha256(file.read_bytes()).hexdigest()})
report={"sourceCommit":head,"frameCount":len(manifest["frames"]),"complete":True,"domain":"ipnetsecurity.com","deploymentVerified":False,"files":files}
(dest/"delivery.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
