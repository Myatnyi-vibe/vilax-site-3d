# Собирает v4/index.html: разметка VILAX (v4/src.html) + WebGL-фон версии 4 (v4/webgl.html).
# webgl.html — блок шаблона «3дсайтпро» с цветами VILAX (как в корневом build.py) и сюжетом «нити → знак V → две завесы → аврора».
# Запуск: python -I v4/build.py
import pathlib, re

here = pathlib.Path(__file__).parent
src = (here / 'src.html').read_text(encoding='utf-8')
gl = (here / 'webgl.html').read_text(encoding='utf-8').rstrip('\n')

out = src.replace('<!--WEBGL-->', gl)
assert '<!--WEBGL-->' not in out

# версия лежит в подпапке: пути от корня сайта сломаются, общие файлы v3 берём через ../ и они должны существовать
bad = re.findall(r'(?:src|href)="/(?!/)[^"]*"', out)
assert not bad, bad
for p in sorted(set(re.findall(r'(?:src|href)="(\.\./[^"#?]+)"', out))):
    assert (here / p).exists(), p

(here / 'index.html').write_text(out, encoding='utf-8')
print('v4/index.html', len(out))
