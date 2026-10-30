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
    assert gl.count(old) == 1, (gl.count(old), old)   # ровно одно место: если шаблон поменяется, правка не уйдёт молча в другой шейдер
    gl = gl.replace(old, new)

# цвета бренда: бирюза, синий, фиолетовый из знака; фон navy0 добавляется в шейдере сияния
sub("uLime: { value: new THREE.Color('#c8f25a') },", "uLime: { value: new THREE.Color('#18f2df') },")
sub("uTeal: { value: new THREE.Color('#5fb7d4') },",
    "uTeal: { value: new THREE.Color('#2297ff') },\n"
    "    uViolet: { value: new THREE.Color('#7a5cc7') },\n"
    "    uBase: { value: new THREE.Color('#081532') }, // фон VILAX (синий логотипа, потемнее): прибавляется к чёрной очистке, чтобы не попасть на двойной sRGB")
sub("uniform float uIntensity;\n        uniform vec3 uLime; uniform vec3 uTeal;\n", "uniform float uIntensity;\n        uniform vec3 uLime; uniform vec3 uTeal; uniform vec3 uBase;\n")
sub("gl_FragColor = vec4(min(col, vec3(1.2)) * amount, 1.0);", "gl_FragColor = vec4(min(col, vec3(1.2)) * amount + uBase, 1.0);")
sub("uniform float uIntensity; uniform vec3 uLime; uniform vec3 uTeal;",
    "uniform float uIntensity; uniform vec3 uLime; uniform vec3 uTeal; uniform vec3 uViolet;")
sub("vC = mix(uLime, uTeal, step(0.8, aSeed));",
    "vC = mix(uLime, uTeal, step(0.62, aSeed));\n          vC = mix(vC, uViolet, step(0.9, aSeed));")

# светлая тема (переключатель в шапке) — рисует сам движок, как в v4/webgl.html: белый фон без вуали и bloom,
# нити ложатся краской цветов знака (обычное смешивание вместо сложения света), без бирюзы; тёмная тема — как была
sub("    uRes: { value: new THREE.Vector2(1, 1) },\n",
    "    uRes: { value: new THREE.Vector2(1, 1) },\n"
    "    uLight: { value: 0 },                         // светлая тема: нити — краской цветов знака на белом, без вуали и bloom (см. __setLight)\n"
    "    uHead: { value: new THREE.Vector4(2, 2, 2, 2) }, // телефон, светлая тема: заголовок hero на экране (x0, y0, x1, y1 в NDC) — под ним нити тише\n")
sub("  };\n\n  // --- мягкое сияние",
    "  };\n  let veil, lines, dust;                          // слои фона — светлая тема переключает их смешивание и видимость\n\n  // --- мягкое сияние")
sub("    const q = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), m);\n    q.frustumCulled = false; q.renderOrder = -1;\n    scene.add(q);",
    "    veil = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), m);\n    veil.frustumCulled = false; veil.renderOrder = -1;\n    scene.add(veil);")
sub("uniform float uIntensity; uniform vec3 uLime; uniform vec3 uTeal; uniform vec3 uViolet;",
    "uniform float uIntensity; uniform vec3 uLime; uniform vec3 uTeal; uniform vec3 uViolet; uniform float uLight; uniform vec4 uHead;")
sub("* (1.0 - 0.72*uW.y);",
    "* (1.0 - mix(0.72, 0.4, uLight)*uW.y);   // на белом вуали нет — нити авроры тушим меньше\n"
    "          if (uLight > 0.5 && uHead.x < 1.5) {   // телефон, светлая: под заголовком hero нити вдвое тише — не сливаются с «в одном окне.»\n"
    "            vec2 ndc = gl_Position.xy / gl_Position.w;\n"
    "            vec2 th = smoothstep(uHead.xy - 0.03, uHead.xy + 0.03, ndc) * (1.0 - smoothstep(uHead.zw - 0.03, uHead.zw + 0.03, ndc));\n"
    "            vA *= 1.0 - 0.5 * th.x * th.y;\n"
    "          }")
sub("vC = mix(vC, vec3(1.0), pulse*0.35);", "vC = mix(vC, uLight > 0.5 ? vC * 0.6 : vec3(1.0), pulse*0.35);   // бегущий свет: на тёмном — белее, на белом — гуще краска")
sub("        varying float vA; varying vec3 vC;\n        void main(){ gl_FragColor = vec4(vC * vA * 0.085, 1.0); }`,",
    "        uniform float uLight;\n        varying float vA; varying vec3 vC;\n"
    "        // тёмная тема — свет складывается (сияние дорисует bloom); светлая — краска цвета нити, плотность по её яркости:\n"
    "        // кривая с насыщением — тусклые нити (их на тёмном держало свечение) заметнее, яркие не заливают пучки\n"
    "        void main(){ gl_FragColor = uLight > 0.5 ? vec4(vC, 1.0 - exp(-vA * 0.5)) : vec4(vC * vA * 0.085, 1.0); }`,")
sub("    scene.add(new THREE.LineSegments(g, m));", "    lines = new THREE.LineSegments(g, m);\n    scene.add(lines);")
sub("        uniform vec3 uLime; varying float vA;\n", "        uniform vec3 uLime; uniform float uLight; varying float vA;\n")
sub("gl_FragColor = vec4(mix(uLime, vec3(1.0), 0.5) * a * vA * 0.35, 1.0);",
    "gl_FragColor = uLight > 0.5 ? vec4(uLime, a * vA * 0.2) : vec4(mix(uLime, vec3(1.0), 0.5) * a * vA * 0.35, 1.0);")
sub("    scene.add(new THREE.Points(g, m));", "    dust = new THREE.Points(g, m);\n    scene.add(dust);")
sub("  window.__three = { scene, uniforms, bloom, composer }; // для отладки и скриптов проверки\n",
    "  window.__three = { scene, uniforms, bloom, composer }; // для отладки и скриптов проверки\n\n"
    "  // --- светлая тема (переключатель в шапке): белый фон без вуали и bloom, нити — краской цветов знака (как --brand-grad светлой темы);\n"
    "  // краска ложится обычным смешиванием, а не сложением света: на пересечениях цвет не белеет и не чернеет\n"
    "  const INK = { uLime: '#2d84c6', uTeal: '#3f68d6', uViolet: '#6a37a6' }, GLOW = {};\n"
    "  for (const k in INK) { GLOW[k] = uniforms[k].value.clone(); INK[k] = new THREE.Color(INK[k]); }\n"
    "  window.__setLight = on => {\n"
    "    uniforms.uLight.value = on ? 1 : 0;\n"
    "    for (const k in INK) uniforms[k].value.copy(on ? INK[k] : GLOW[k]);\n"
    "    bloom.enabled = !on; veil.visible = !on;\n"
    "    lines.material.blending = dust.material.blending = on ? THREE.NormalBlending : THREE.AdditiveBlending;\n"
    "    renderer.setClearColor(on ? 0xffffff : 0x000000, 1);\n"
    "  };\n"
    "  window.__setLight(document.documentElement.getAttribute('data-theme') === 'light');\n")
sub("    camera.lookAt(0, 0, 0);\n    composer.render();",
    "    camera.lookAt(0, 0, 0);\n"
    "    if (mobile && uniforms.uLight.value > 0.5 && heroH1) {   // телефон, светлая: заголовок hero на экране — маска uHead\n"
    "      const r = heroH1.getBoundingClientRect();\n"
    "      if (r.bottom > 0 && r.top < innerHeight) uniforms.uHead.value.set(r.left / innerWidth * 2 - 1, 1 - 2 * r.bottom / innerHeight, r.right / innerWidth * 2 - 1, 1 - 2 * r.top / innerHeight);\n"
    "      else uniforms.uHead.value.set(2, 2, 2, 2);\n"
    "    }\n"
    "    composer.render();")
sub("  const clock = new THREE.Clock();", "  const heroH1 = document.querySelector('.hero h1');\n  const clock = new THREE.Clock();")

out = src.replace('<!--WEBGL-->', gl)
assert '<!--WEBGL-->' not in out
(here / 'index.html').write_text(out, encoding='utf-8')
print('index.html', len(out))
