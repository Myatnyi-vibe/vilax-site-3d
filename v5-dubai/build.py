# Builds v5-dubai/index.html: VILAX EN/AED markup (v5-dubai/src.html) + the WebGL background from v4 (v5-dubai/webgl.html).
# webgl.html is the threads/V-mark scene of the 3D template in VILAX colours, unchanged from v4.
# Run: python -I v5-dubai/build.py
import pathlib, re

here = pathlib.Path(__file__).parent
src = (here / 'src.html').read_text(encoding='utf-8')
gl = (here / 'webgl.html').read_text(encoding='utf-8').rstrip('\n')

out = src.replace('<!--WEBGL-->', gl)
assert '<!--WEBGL-->' not in out

# the version lives in a subfolder: root-absolute paths would break; shared files are referenced via ../ and must exist
bad = re.findall(r'(?:src|href)="/(?!/)[^"]*"', out)
assert not bad, bad
for p in sorted(set(re.findall(r'(?:src|href)="(\.\./[^"#?]+)"', out))):
    assert (here / p).exists(), p

(here / 'index.html').write_text(out, encoding='utf-8')
print('v5-dubai/index.html', len(out))
