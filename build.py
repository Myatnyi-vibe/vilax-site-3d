# Собирает index.html: разметка VILAX (src.html) + WebGL-фон из шаблона «3дсайтпро» с цветами VILAX.
# Запуск: python -I build.py
import os, pathlib, re

here = pathlib.Path(__file__).parent
# шаблон WebGL-фона; другой путь — переменной окружения VILAX3D_TEMPLATE
tpl_path = pathlib.Path(os.environ.get('VILAX3D_TEMPLATE') or pathlib.Path.home() / '.claude' / 'skills' / '3d-sayt-pro' / 'template' / 'index.html')
tpl = tpl_path.read_text(encoding='utf-8')
src = (here / 'src.html').read_text(encoding='utf-8')

m = re.search(r'<!-- ============ WEBGL: СВЕТЯЩИЕСЯ НИТИ ============ -->.*?</script>', tpl, re.S)
gl = m.group(0)

def sub(old, new):
    global gl
    assert old in gl, old
    gl = gl.replace(old, new, 1)

# цвета бренда: бирюза, синий, фиолетовый из знака; фон navy0 добавляется в шейдере сияния
sub("uLime: { value: new THREE.Color('#c8f25a') },", "uLime: { value: new THREE.Color('#18f2df') },")
sub("uTeal: { value: new THREE.Color('#5fb7d4') },",
    "uTeal: { value: new THREE.Color('#2297ff') },\n"
    "    uViolet: { value: new THREE.Color('#7a5cc7') },\n"
    "    uBase: { value: new THREE.Color('#081532') }, // фон VILAX (синий логотипа, потемнее): прибавляется к чёрной очистке, чтобы не попасть на двойной sRGB")
sub("uniform vec3 uLime; uniform vec3 uTeal;\n", "uniform vec3 uLime; uniform vec3 uTeal; uniform vec3 uBase;\n")
sub("gl_FragColor = vec4(min(col, vec3(1.2)) * amount, 1.0);", "gl_FragColor = vec4(min(col, vec3(1.2)) * amount + uBase, 1.0);")
sub("uniform float uIntensity; uniform vec3 uLime; uniform vec3 uTeal;",
    "uniform float uIntensity; uniform vec3 uLime; uniform vec3 uTeal; uniform vec3 uViolet;")
sub("vC = mix(uLime, uTeal, step(0.8, aSeed));",
    "vC = mix(uLime, uTeal, step(0.62, aSeed));\n          vC = mix(vC, uViolet, step(0.9, aSeed));")

out = src.replace('<!--WEBGL-->', gl)
assert '<!--WEBGL-->' not in out
(here / 'index.html').write_text(out, encoding='utf-8')
print('index.html', len(out))
