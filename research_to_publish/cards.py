"""Optional PNG output via Pillow. Text layout checked against actual font metrics."""
from pathlib import Path
from .core import read_json, nonempty


def lines(text, font, max_width):
    result = []
    for para in text.splitlines():
        line = ''
        for char in para:
            if font.getlength(line + char) > max_width and line:
                result.append(line)
                line = ''
            line += char
        result.append(line)
    return result


def rasterize(package, output, font_path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise ValueError('PNG output requires Pillow: pip install "research-to-publish[images]"')
    package, output = Path(package), Path(output)
    if output.exists():
        raise ValueError('PNG output directory must not exist')
    data = read_json(package / 'xiaohongshu.json')
    title_font = ImageFont.truetype(str(font_path), 64)
    body_font = ImageFont.truetype(str(font_path), 40)
    small_font = ImageFont.truetype(str(font_path), 28)
    images = []
    for n, card in enumerate(data['cards'], 1):
        title = lines(nonempty(card['heading'], 'heading'), title_font, 920)
        body = lines(nonempty(card['body'], 'body'), body_font, 920)
        if len(title) > 3 or len(body) > 16:
            raise ValueError('PNG card overflow; shorten content and rebuild')
        im = Image.new('RGB', (1080, 1440), '#f5f1e8')
        d = ImageDraw.Draw(im)
        d.rectangle((80, 90, 170, 102), fill='#bd5033')
        for i, line in enumerate(title):
            d.text((80, 150 + i * 86), line, fill='#252823', font=title_font)
        for i, line in enumerate(body):
            d.text((80, 470 + i * 44), line, fill='#252823', font=body_font)
        d.text((80, 1310), '%02d / %02d' % (n, len(data['cards'])), fill='#252823', font=small_font)
        images.append(im)
    output.mkdir(parents=True)
    for n, im in enumerate(images, 1):
        im.save(output / ('%02d.png' % n))
    return {'png_directory': str(output.resolve()), 'cards': len(images), 'size': [1080, 1440]}
