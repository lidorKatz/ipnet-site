"""Fetch a pinned, checksum-verified optional local CPU denoiser.

Does not modify system packages or website dependencies. Network access is
only to the official RenderKit/oidn GitHub release. No keys or uploads.
"""
from pathlib import Path
import hashlib
import tarfile
import urllib.request

target = Path('/tmp/ipnet-render-tools')
target.mkdir(parents=True, exist_ok=True)
archive = target / 'oidn-2.5.1.x86_64.linux.tar.gz'
url = 'https://github.com/RenderKit/oidn/releases/download/v2.5.1/oidn-2.5.1.x86_64.linux.tar.gz'
expected = '743c3e2aff8c220d5d70fe6cb970fb3d36f2702d2693c61d1d148e404cf37cd6'
if not archive.exists():
    with urllib.request.urlopen(url, timeout=90) as response, archive.open('wb') as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
actual = hashlib.sha256(archive.read_bytes()).hexdigest()
if actual != expected:
    raise SystemExit('Official OIDN archive checksum mismatch; not extracting or executing.')
with tarfile.open(archive) as source:
    source.extractall(target, filter='data')
binary = target / 'oidn-2.5.1.x86_64.linux/bin/oidnDenoise'
assert hashlib.sha256(binary.read_bytes()).hexdigest() == '1cb3a28ebc99b90d7548b0b8b16f70c163cb59abe8582458a254aa303338269c'
print('Verified optional authoring tool:', binary)
