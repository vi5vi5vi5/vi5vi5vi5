#!/usr/bin/env python3
"""
Генератор картинок для профиля GitHub в стиле инженерного чертежа.

    pip install fonttools
    python build.py

Собирает в assets/ шапку, карточки проектов и спецификацию стека,
каждую в светлой («калька») и тёмной («синька») теме.

Текст переводится в кривые: GitHub показывает SVG как картинку,
и внешние шрифты в ней не грузятся. Шрифт — JetBrains Mono (OFL),
скачивается в .fonts/ при первом запуске.

Всё, что стоит поменять под себя, — в блоке НАСТРОЙКИ ниже.
"""
import math
import os
import urllib.request
from html import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

# ───────────────────────── НАСТРОЙКИ ─────────────────────────

HANDLE = "vi5vi5vi5"
NAME = "Vi5"                       # крупная надпись в шапке
ROLE = "backend-разработчик"
FOCUS = "сетевые сервисы · realtime · self-hosted"
LANGS = "C++20 · Python · C# · "   # перед «Go», который обведён красным
LEARNING = "Go"
ORG = "РХТУ им. Менделеева"
CODE = "VI5.GH.001"               # «обозначение» документа в штампе

SPEC = [  # спецификация: раздел или (обозначение, наименование, примечание)
    "Языки",
    ("C++20", "серверы, CLI, нативные клиенты", "Ferry, MeetUp"),
    ("Python", "скрипты, автоматизация, сервисы", ""),
    ("C#", "прикладные приложения, Web API", ""),
    ("Go", "бэкенд-сервисы", "!изучаю"),
    "Сети и безопасность",
    ("WebSocket · HTTP API", "свои протоколы с документацией", "docs/protocol.md"),
    ("TLS · nginx · Let's Encrypt", "HTTPS, общий прокси на несколько сервисов", ""),
    ("AES-256-GCM · HKDF", "сквозное шифрование на устройстве", "Ferry, MeetUp"),
    ("BLAKE3 · Argon2id", "целостность тома, ключ из пароля", "Ferry"),
    "Инфраструктура",
    ("Docker · compose", "развёртывание одной командой", ""),
    ("Linux · VPS", "свои сервисы в продакшене", "meetup.fferry.ru"),
    ("CMake · MinGW-w64", "кроссборка Linux → Windows", "Ferry"),
    ("SQLite", "аккаунты и комнаты", "MeetUp"),
]

THEMES = {
    "light": dict(  # калька
        bg="#F4F0E6", grid="#E6DFCF", grid_major="#D8CEB8", ink="#1E2833",
        muted="#6A675E", faint="#A8A192", accent="#C63D2A", node="#FBF9F4",
    ),
    "dark": dict(  # синька
        bg="#0E2B4A", grid="#163A60", grid_major="#1E4A77", ink="#E4EDF7",
        muted="#9CB3CB", faint="#5D7FA4", accent="#FFB547", node="#113457",
    ),
}

# ─────────────────────────── ШРИФТ ───────────────────────────

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "assets")
FONT_DIR = os.path.join(ROOT, ".fonts")
FONT_URL = "https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/fonts/ttf/{}.ttf"
FONT_FILES = {"r": "JetBrainsMono-Regular", "b": "JetBrainsMono-Bold",
              "x": "JetBrainsMono-ExtraBold", "i": "JetBrainsMono-Italic"}


class Font:
    def __init__(self, key, name):
        path = os.path.join(FONT_DIR, name + ".ttf")
        if not os.path.exists(path):
            os.makedirs(FONT_DIR, exist_ok=True)
            print("скачиваю", name)
            urllib.request.urlretrieve(FONT_URL.format(name), path)
        f = TTFont(path)
        self.key = key
        self.glyphs = f.getGlyphSet()
        self.cmap = f.getBestCmap()
        self.upm = f["head"].unitsPerEm
        self.adv = f["hmtx"][self.cmap[ord("a")]][0]  # моноширинный
        self.cache = {}

    def outline(self, ch):
        if ch not in self.cache:
            name = self.cmap.get(ord(ch))
            if name is None:
                raise SystemExit(f"в шрифте {self.key} нет символа {ch!r}")
            pen = SVGPathPen(self.glyphs, ntos=lambda v: "%d" % round(v))
            self.glyphs[name].draw(pen)
            self.cache[ch] = pen.getCommands()
        return self.cache[ch]


FONTS = {}


def font(key):
    if key not in FONTS:
        FONTS[key] = Font(key, FONT_FILES[key])
    return FONTS[key]


def tw(s, size):
    """Ширина строки моноширинным шрифтом."""
    return len(s) * 0.6 * size


# ─────────────────────────── ХОЛСТ ───────────────────────────

class Doc:
    def __init__(self, w, h, t, title):
        self.w, self.h, self.t, self.title = w, h, t, title
        self.glyphs, self.defs, self.body = {}, [], []

    def add(self, *parts):
        self.body.extend(parts)

    def text(self, s, x, y, size, f="r", fill=None, anchor="start"):
        F = font(f)
        k = size / F.upm
        if anchor == "middle":
            x -= tw(s, size) / 2
        elif anchor == "end":
            x -= tw(s, size)
        uses = []
        for i, ch in enumerate(s):
            if ch == " ":
                continue
            gid = f"{f}{ord(ch):x}"
            if gid not in self.glyphs:
                self.glyphs[gid] = F.outline(ch)
            uses.append(f'<use href="#{gid}" x="{i * F.adv}"/>')
        return (f'<g fill="{fill or self.t["ink"]}" transform="translate({x:.1f} {y:.1f}) '
                f'scale({k:.4f} {-k:.4f})">{"".join(uses)}</g>')

    def render(self):
        glyphs = "".join(f'<path id="{k}" d="{v}"/>' for k, v in self.glyphs.items())
        t = escape(self.title)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img" aria-label="{t}">'
                f'<title>{t}</title><defs>{glyphs}{"".join(self.defs)}</defs>'
                f'{"".join(self.body)}</svg>\n')


def rect(x, y, w, h, stroke="none", sw=1, fill="none", rx=0, dash=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>')


def line(x1, y1, x2, y2, stroke, sw=1, dash=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}{extra}/>')


def path(d, stroke, sw=1, fill="none", extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'


def sheet(doc, left=40, m=14):
    """Лист: бумага, миллиметровка, рамка с полем для подшивки."""
    t, W, H = doc.t, doc.w, doc.h
    doc.defs.append(
        f'<pattern id="g1" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<path d="M20 0H0V20" fill="none" stroke="{t["grid"]}" stroke-width="0.6"/></pattern>'
        f'<pattern id="g5" width="100" height="100" patternUnits="userSpaceOnUse">'
        f'<rect width="100" height="100" fill="url(#g1)"/>'
        f'<path d="M100 0H0V100" fill="none" stroke="{t["grid_major"]}" stroke-width="1"/></pattern>'
        f'<marker id="arr" viewBox="0 0 12 10" refX="12" refY="5" markerWidth="12" markerHeight="10" '
        f'markerUnits="userSpaceOnUse" orient="auto-start-reverse">'
        f'<path d="M0 3.3L12 5L0 6.7z" fill="{t["ink"]}"/></marker>'
    )
    doc.add(rect(0, 0, W, H, fill=t["bg"]),
            rect(left, m, W - left - m, H - 2 * m, fill="url(#g5)"),
            rect(5.5, 5.5, W - 11, H - 11, t["faint"], 0.6, dash="2 4"),
            rect(left, m, W - left - m, H - 2 * m, t["ink"], 2.4))


def dim_h(doc, x1, x2, y, label, ext_from=None, size=14, above=False):
    """Горизонтальный размер со стрелками и выносными линиями."""
    t = doc.t
    out = []
    if ext_from is not None:
        for x in (x1, x2):
            out.append(line(x, ext_from, x, y + 6, t["ink"], 0.7))
    out.append(line(x1, y, x2, y, t["ink"], 0.8,
                    extra=' marker-start="url(#arr)" marker-end="url(#arr)"'))
    ty = y - 7 if above else y + size + 4
    out.append(doc.text(label, (x1 + x2) / 2, ty, size, "i", t["muted"], "middle"))
    doc.add(*out)


def dim_v(doc, x, y1, y2, label, ext_from=None, size=15):
    t = doc.t
    out = []
    if ext_from is not None:
        for y in (y1, y2):
            out.append(line(ext_from, y, x + 6, y, t["ink"], 0.7))
    out.append(line(x, y1, x, y2, t["ink"], 0.8,
                    extra=' marker-start="url(#arr)" marker-end="url(#arr)"'))
    cy = (y1 + y2) / 2
    out.append(f'<g transform="rotate(-90 {x} {cy})">'
               f'{doc.text(label, x, cy - 6, size, "i", t["ink"], "middle")}</g>')
    doc.add(*out)


def pencil_ellipse(cx, cy, rx, ry, color, sw=1.8, seed=1.0):
    """Обводка «от руки» красным карандашом: чуть неровная и с нахлёстом."""
    pts = []
    n = 40
    for i in range(n + 6):
        a = -2.4 + i * (2 * math.pi + 0.55) / n
        j = 1 + 0.045 * math.sin(a * 3 + seed) + 0.03 * math.sin(a * 5 + seed * 2)
        pts.append((cx + rx * j * math.cos(a), cy + ry * j * math.sin(a) - i * 0.06))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return path(d, color, sw, extra=' stroke-linecap="round" stroke-linejoin="round" opacity="0.9"')


def node(doc, x, y, w, h, label, size=15, f="r", dx=None):
    t = doc.t
    tx = x + w / 2 if dx is None else x + dx
    anchor = "middle" if dx is None else "start"
    return (rect(x, y, w, h, t["ink"], 1.4, t["node"])
            + doc.text(label, tx, y + h / 2 + size * 0.36, size, f, t["ink"], anchor))


def mover(d, dur, begin, start, end, fill, size=9):
    """Пакет, который проходит путь d в доле цикла [start, end] и прячется в остальное время."""
    vis = f'values="0;1;0" keyTimes="0;{start};{end}"' if start > 0 else f'values="1;0" keyTimes="0;{end}"'
    h = size / 2
    return (f'<rect x="{-h}" y="{-h}" width="{size}" height="{size}" fill="{fill}" opacity="0">'
            f'<animateMotion path="{d}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite" '
            f'calcMode="linear" keyTimes="0;{start};{end};1" keyPoints="0;0;1;1"/>'
            f'<animate attributeName="opacity" {vis} calcMode="discrete" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="indefinite"/></rect>')


def stream(inbound, outbound, fill, dur=2.4, waves=3, size=9):
    """Волны пакетов: сначала по входящему пути, потом копии по всем исходящим разом."""
    out = []
    for w in range(waves):
        b = -w * dur / waves  # отрицательный begin — поток идёт с первого кадра
        out.append(mover(inbound, dur, b, 0, 0.42, fill, size))
        for d in outbound:
            out.append(mover(d, dur, b, 0.5, 0.92, fill, size))
    return "".join(out)


def stamp(doc, cx, cy, big, small, angle=-8):
    """Печать: двойная рамка, поворот, полупрозрачность."""
    t = doc.t
    a = t["accent"]
    w, h = 118, 58
    return (f'<g transform="rotate({angle} {cx} {cy})" opacity="0.88">'
            + rect(cx - w / 2, cy - h / 2, w, h, a, 2, rx=6)
            + rect(cx - w / 2 + 4, cy - h / 2 + 4, w - 8, h - 8, a, 0.9, rx=4)
            + doc.text(big, cx, cy + 5, 24, "x", a, "middle")
            + doc.text(small, cx, cy + 21, 11, "i", a, "middle")
            + "</g>")


def mini_block(doc, x2, y2, code, sheet_no):
    """Маленький штамп в углу карточки."""
    t = doc.t
    x1, y1 = x2 - 186, y2 - 34
    mid = x1 + 116
    doc.add(rect(x1, y1, x2 - x1, y2 - y1, t["ink"], 1.6, t["node"]),
            line(mid, y1, mid, y2, t["ink"], 0.9),
            doc.text(code, (x1 + mid) / 2, y1 + 22, 14, "b", t["ink"], "middle"),
            doc.text(f"Лист {sheet_no}", (mid + x2) / 2, y1 + 22, 13, "i", t["muted"], "middle"))


# ─────────────────────────── ШАПКА ───────────────────────────

def header(t):
    W, H = 1200, 460
    d = Doc(W, H, t, f"{NAME} — {ROLE}: {FOCUS}. Схема: отправитель → релей → N получателей")
    sheet(d)
    ink, mu, ac = t["ink"], t["muted"], t["accent"]

    # Поле подшивки слева: графы, как на настоящем листе.
    cells = [(446, 370, "Инв. № подл."), (370, 300, "Подп. и дата"), (300, 236, "Взам. инв. №")]
    for y2, y1, lab in cells:
        cy = (y1 + y2) / 2
        d.add(rect(14, y1, 26, y2 - y1, ink, 1),
              f'<g transform="rotate(-90 27 {cy})">{d.text(lab, 27, cy + 3, 8, "i", mu, "middle")}</g>')

    # Левый блок: кто это.
    X = 80
    d.add(d.text("ЛИСТ 1 · ОБЩИЙ ВИД · М 1:1", X, 78, 14, "i", mu))
    d.add(d.text(NAME, X - 6, 212, 132, "x", ink))
    name_w = tw(NAME, 132) - 14
    dim_h(d, X, X + name_w, 242, HANDLE, ext_from=224, size=14)
    d.add(d.text(ROLE, X, 312, 30, "b", ink))
    d.add(d.text(FOCUS, X, 346, 18, "r", mu))
    d.add(d.text(LANGS + LEARNING, X, 390, 18, "r", ink))
    gx = X + tw(LANGS, 18) + tw(LEARNING, 18) / 2
    d.add(pencil_ellipse(gx, 384, 25, 16, ac, seed=0.7))
    d.add(d.text("← учу", gx + 32, 391, 16, "i", ac))

    # Схема: отправитель → релей → N получателей.
    d.add(d.text("СХЕМА СТРУКТУРНАЯ", 590, 70, 14, "i", mu))
    sx, sy, sw_, sh = 590, 150, 120, 56
    rx, ry, rw, rh = 790, 128, 132, 100
    cy = 178
    recv = [(1020, 92), (1020, 156), (1020, 220)]
    rcw, rch = 120, 44

    inbound = f"M{sx + sw_} {cy} H{rx}"
    outs = [f"M{rx + rw} {cy} H{rx + rw + 46} V{y + rch / 2} H{x}" for x, y in recv]
    d.add(path(inbound, ink, 1.4), *[path(o, ink, 1.4) for o in outs])
    d.add(f'<circle cx="{rx + rw + 46}" cy="{cy}" r="3.2" fill="{ink}"/>')

    d.add(node(d, sx, sy, sw_, sh, "отправитель", 15))
    d.add(rect(rx, ry, rw, rh, ink, 2.2, t["node"]),
          d.text("РЕЛЕЙ", rx + rw / 2, ry + 30, 18, "b", ink, "middle"))
    # окно чанков в оперативке
    for i in range(6):
        x = rx + 19 + i * 16
        on = 1 <= i <= 4
        d.add(rect(x, ry + 44, 12, 12, ac if on else t["faint"], 1.2, ac if on else "none"))
    d.add(path(f"M{rx + 32} {ry + 62} v5 H{rx + 98} v-5", ac, 1.1))
    d.add(d.text("RAM", rx + rw / 2, ry + 80, 12, "i", ac, "middle"))
    d.add(d.text("диск: 0 B", rx + rw / 2, ry + rh + 22, 14, "i", mu, "middle"))
    labels = ["получатель 1", "получатель 2", "получатель N"]
    for (x, y), lab in zip(recv, labels):
        d.add(node(d, x, y, rcw, rch, lab, 14))

    d.add(stream(inbound, outs, ac))

    # выноски и размеры
    d.add(path(f"M{rx + rw / 2} {ry} V{ry - 26}", ink, 0.8),
          d.text("видит только шифротекст", rx + rw / 2, ry - 32, 14, "i", ink, "middle"))
    d.add(d.text("AES-256-GCM", sx + sw_ / 2, sy - 14, 13, "i", ac, "middle"))
    d.add(d.text("1× отдача", sx + sw_ / 2, sy + sh + 24, 14, "i", mu, "middle"))
    dim_v(d, 1164, recv[0][1], recv[-1][1] + rch, "N", ext_from=1144)

    # Основная надпись (штамп).
    x1, x2, y1, y2 = 706, 1186, 330, 446
    rows = [y1 + i * 29 for i in range(5)]
    xa, xb, xc = 770, 900, 1036
    d.add(rect(x1, y1, x2 - x1, y2 - y1, ink, 2.4, t["node"]))
    for y in rows[1:-1]:
        d.add(line(x1, y, xb, y, ink, 0.8))
    d.add(line(xa, y1, xa, y2, ink, 0.8), line(xb, y1, xb, y2, ink, 2.2),
          line(xb, 388, x2, 388, ink, 2.2), line(xc, 388, xc, y2, ink, 1.6),
          line(xc, 406, x2, 406, ink, 0.8), line(xc, 424, x2, 424, ink, 0.8))
    for i in (1, 2):
        d.add(line(xc + 50 * i, 388, xc + 50 * i, 424, ink, 0.8))
    meta = [("Разраб.", NAME), ("Профиль", "backend"), ("Стек", "C++ · Py"), ("Учу", LEARNING)]
    for (lab, val), y in zip(meta, rows):
        d.add(d.text(lab, x1 + 7, y + 19, 12, "i", mu),
              d.text(val, xa + 8, y + 20, 14, "r", ac if lab == "Учу" else ink))
    d.add(d.text(CODE, (xb + x2) / 2, 368, 24, "b", ink, "middle"))
    d.add(d.text("Профиль", (xb + xc) / 2, 412, 14, "r", ink, "middle"),
          d.text("разработчика", (xb + xc) / 2, 432, 14, "r", ink, "middle"))
    for i, (h, v) in enumerate([("Лит.", "У"), ("Лист", "1"), ("Листов", "3")]):
        cx = xc + 25 + 50 * i
        d.add(d.text(h, cx, 401, 10.5, "i", mu, "middle"),
              d.text(v, cx, 420, 13, "b", ink, "middle"))
    d.add(d.text(ORG, (xc + x2) / 2, 440, 11.5, "r", ink, "middle"))
    return d


# ────────────────────────── КАРТОЧКИ ─────────────────────────

def card_base(t, title, sheet_no, name, sub):
    d = Doc(600, 420, t, title)
    sheet(d, left=14, m=14)
    d.add(d.text(f"ЛИСТ {sheet_no} · {name.upper()}", 40, 50, 13, "i", t["muted"]),
          d.text(name, 36, 100, 50, "x", t["ink"]),
          d.text(sub, 40, 132, 17, "r", t["ink"]))
    return d


def card_ferry(t):
    ink, mu, ac = t["ink"], t["muted"], t["accent"]
    d = card_base(t, "Ferry — релей больших файлов без хранения, со сквозным шифрованием",
                  2, "Ferry", "релей больших файлов без хранения")
    d.add(stamp(d, 500, 76, "E2E", "0 B на диске"))

    # Поток чанков через окно в оперативке релея.
    L, R, y0, pitch, cs = 40, 560, 196, 28, 20
    wx1, wx2 = 232, 372
    d.defs.append(f'<clipPath id="strip"><rect x="{L}" y="{y0 - 8}" width="{R - L}" height="{cs + 16}"/></clipPath>'
                  f'<clipPath id="win"><rect x="{wx1}" y="{y0 - 8}" width="{wx2 - wx1}" height="{cs + 16}"/></clipPath>')
    xs = range(L - 2 * pitch, R + pitch, pitch)
    anim = (f'<animateTransform attributeName="transform" type="translate" from="0 0" '
            f'to="{pitch} 0" dur="0.7s" repeatCount="indefinite"/>')
    ghost = "".join(rect(x + 4, y0, cs, cs, t["faint"], 1.1, dash="3 2.5") for x in xs)
    solid = "".join(rect(x + 4, y0, cs, cs, ac, 1, ac) for x in xs)
    d.add(f'<g clip-path="url(#strip)"><g>{ghost}{anim}</g></g>',
          f'<g clip-path="url(#win)"><g>{solid}{anim}</g></g>')
    d.add(rect(wx1, y0 - 10, wx2 - wx1, cs + 20, ac, 2, rx=3))
    d.add(d.text("окно в RAM", (wx1 + wx2) / 2, y0 - 20, 14, "i", ac, "middle"),
          d.text("от отправителя", L, y0 - 20, 13, "i", mu),
          d.text("к получателям", R, y0 - 20, 13, "i", mu, "end"))
    dim_h(d, wx1, wx2, y0 + cs + 26, "на диск не пишется", ext_from=y0 + cs + 12, size=13)

    # Почему не P2P.
    d.add(d.text("скорость у каждого из N получателей", 40, 300, 13, "i", mu),
          d.text("P2P", 40, 328, 16, "r", mu),
          d.text("аплоад / N", 120, 328, 16, "r", mu),
          d.text("Ferry", 40, 356, 16, "b", ac),
          d.text("min(аплоад, даунлоад)", 120, 356, 16, "r", ink))
    d.add(line(40, 337, 330, 337, t["faint"], 0.8, dash="2 3"))

    d.add(d.text("C++20 · Qt6 · WebSocket · OpenSSL · Docker", 40, 392, 12.5, "r", mu))
    mini_block(d, 586, 406, "FERRY.001", 2)
    return d


def card_meetup(t):
    ink, mu, ac = t["ink"], t["muted"], t["accent"]
    d = card_base(t, "MeetUp — видеозвонки на своём сервере, со сквозным шифрованием",
                  3, "MeetUp", "видеозвонки на своём сервере")
    d.add(stamp(d, 500, 76, "LIVE", "демо онлайн", angle=6))

    # Комната: четыре участника вокруг релея.
    pw, ph = 110, 40
    parts = [(40, 158, "браузер"), (40, 226, "Windows"), (450, 158, "телефон"), (450, 226, "браузер")]
    rx, ry, rw, rh = 245, 180, 110, 66
    cy = ry + rh / 2
    paths = []
    for x, y, _ in parts:
        py = y + ph / 2
        if x < rx:
            paths.append(f"M{x + pw} {py} H{rx - 44} V{cy - 10 if py < cy else cy + 10} H{rx}")
        else:
            paths.append(f"M{rx + rw} {cy - 10 if py < cy else cy + 10} H{rx + rw + 44} V{py} H{x}")
    d.add(*[path(p, ink, 1.3) for p in paths])
    for i, (x, y, lab) in enumerate(parts):
        d.add(node(d, x, y, pw, ph, lab, 13, dx=10))
    d.add(rect(rx, ry, rw, rh, ink, 2.2, t["node"]),
          d.text("РЕЛЕЙ", rx + rw / 2, ry + 30, 16, "b", ink, "middle"),
          d.text("кадры не", rx + rw / 2, ry + 47, 11, "i", mu, "middle"),
          d.text("вскрывает", rx + rw / 2, ry + 60, 11, "i", mu, "middle"))

    # Говорит первый участник: эквалайзер и поток к остальным.
    bx, by = 128, 158 + ph / 2
    for i, hs in enumerate(["4;16;7;13;4", "8;5;16;6;8", "5;13;4;15;5", "10;6;12;4;10"]):
        hv = [float(v) for v in hs.split(";")]
        ys = ";".join(f"{by - h / 2:.1f}" for h in hv)
        d.add(f'<rect x="{bx + i * 5}" y="{by - hv[0] / 2}" width="3" height="{hv[0]}" fill="{ac}">'
              f'<animate attributeName="height" values="{hs}" dur="1.1s" repeatCount="indefinite"/>'
              f'<animate attributeName="y" values="{ys}" dur="1.1s" repeatCount="indefinite"/></rect>')
    inbound = paths[0]
    outs = []
    for p in paths[1:]:
        # исходящие пути развёрнуты: от релея к участнику
        if p.startswith(f"M{rx + rw}"):
            outs.append(p)
        else:
            seg = p[1:].replace("H", " H").replace("V", " V").split()
            x0, y0p = seg[0], seg[1]
            v = seg[3][1:]
            outs.append(f"M{rx} {v} H{rx - 44} V{y0p} H{x0}")
    d.add(stream(inbound, outs, ac, size=8))
    d.add(d.text("шифротекст", rx + rw / 2, ry - 12, 13, "i", ac, "middle"))

    d.add(d.text("сервер пересылает кадры, не заглядывая внутрь", 40, 300, 13, "i", mu),
          d.text("H.264 / VP8 / VP9 · Opus · AES-256-GCM", 40, 328, 15, "r", ink),
          d.text("демо → meetup.fferry.ru", 40, 356, 15, "b", ac))

    d.add(d.text("C++20 · Qt6 · React · WebCodecs · ffmpeg", 40, 392, 12.5, "r", mu))
    mini_block(d, 586, 406, "MEETUP.001", 3)
    return d


# ──────────────────────── СПЕЦИФИКАЦИЯ ───────────────────────

def spec(t):
    ink, mu, ac = t["ink"], t["muted"], t["accent"]
    rh, top, head = 30, 92, 40
    H = top + head + rh * len(SPEC) + 36
    d = Doc(1200, H, t, "Спецификация: языки, сети и безопасность, инфраструктура")
    sheet(d)
    d.add(d.text("СПЕЦИФИКАЦИЯ", 70, 64, 22, "x", ink),
          d.text(f"{CODE} СП · стек и инструменты", 70 + tw("СПЕЦИФИКАЦИЯ ", 22), 64, 14, "i", mu))
    cols = [70, 140, 450, 930, 1160]
    heads = ["Поз.", "Обозначение", "Наименование", "Примечание"]
    y_end = top + head + rh * len(SPEC)
    d.add(rect(cols[0], top, cols[-1] - cols[0], y_end - top, ink, 2.2, t["node"]))
    d.add(line(cols[0], top + head, cols[-1], top + head, ink, 2.2))
    for x in cols[1:-1]:
        d.add(line(x, top, x, y_end, ink, 1.6))
    for i, h in enumerate(heads):
        d.add(d.text(h, (cols[i] + cols[i + 1]) / 2, top + 26, 14, "i", mu, "middle"))
    pos = 0
    for r, row in enumerate(SPEC):
        y = top + head + r * rh
        if r:
            d.add(line(cols[0], y, cols[-1], y, t["grid_major"], 0.8))
        base = y + rh / 2 + 5.5
        if isinstance(row, str):
            cx = (cols[2] + cols[3]) / 2
            d.add(d.text(row, cx, base, 15, "b", ink, "middle"),
                  line(cx - tw(row, 15) / 2, base + 4, cx + tw(row, 15) / 2, base + 4, ink, 1))
            continue
        pos += 1
        code, name, note = row
        hot = note.startswith("!")
        note = note.lstrip("!")
        d.add(d.text(str(pos), (cols[0] + cols[1]) / 2, base, 15, "r", mu, "middle"),
              d.text(code, cols[1] + 12, base, 15, "b" if hot else "r", ac if hot else ink),
              d.text(name, cols[2] + 12, base, 15, "r", ink))
        if note:
            d.add(d.text(note, cols[3] + 12, base, 14, "i", ac if hot else mu))
        if hot:
            d.add(pencil_ellipse(cols[3] + 12 + tw(note, 14) / 2, base - 5, tw(note, 14) / 2 + 9, 12, ac, 1.5, seed=2.1))
    return d


# ─────────────────────────── СБОРКА ──────────────────────────

def main():
    os.makedirs(OUT, exist_ok=True)
    builders = {"header": header, "card-ferry": card_ferry, "card-meetup": card_meetup, "spec": spec}
    for theme, t in THEMES.items():
        for name, fn in builders.items():
            svg = fn(t).render()
            p = os.path.join(OUT, f"{name}-{theme}.svg")
            with open(p, "w", encoding="utf-8") as f:
                f.write(svg)
            print(f"{os.path.relpath(p, ROOT):32} {len(svg.encode()) // 1024:4} КБ")


if __name__ == "__main__":
    main()
