#!/usr/bin/env python3
"""Kozu Spectrum generator (review 0.6). Prints the palette as JSON.

Each Kozu family follows one Tailwind CSS v4 family's OKLCH lightness and chroma per step,
turned by a small Kozu hue offset. Roles are then picked per family by measured WCAG contrast;
a role step is nudged darker or lighter only when it misses its target.

Edit MAP to change a family's base, offset or fill step, then regenerate tokens:
    python3 tools/kozu_spectrum.py > palette.json

Tailwind data: default theme colors of Tailwind CSS v4.0.0, (c) Tailwind Labs, Inc., MIT License.
"""
import json
import math

TAILWIND_V4 = {
    "red": {"50": (0.971, 0.013, 17.38), "100": (0.936, 0.032, 17.717), "200": (0.885, 0.062, 18.334), "300": (0.808, 0.114, 19.571), "400": (0.704, 0.191, 22.216), "500": (0.637, 0.237, 25.331), "600": (0.577, 0.245, 27.325), "700": (0.505, 0.213, 27.518), "800": (0.444, 0.177, 26.899), "900": (0.396, 0.141, 25.723), "950": (0.258, 0.092, 26.042)},
    "orange": {"50": (0.98, 0.016, 73.684), "100": (0.954, 0.038, 75.164), "200": (0.901, 0.076, 70.697), "300": (0.837, 0.128, 66.29), "400": (0.75, 0.183, 55.934), "500": (0.705, 0.213, 47.604), "600": (0.646, 0.222, 41.116), "700": (0.553, 0.195, 38.402), "800": (0.47, 0.157, 37.304), "900": (0.408, 0.123, 38.172), "950": (0.266, 0.079, 36.259)},
    "amber": {"50": (0.987, 0.022, 95.277), "100": (0.962, 0.059, 95.617), "200": (0.924, 0.12, 95.746), "300": (0.879, 0.169, 91.605), "400": (0.828, 0.189, 84.429), "500": (0.769, 0.188, 70.08), "600": (0.666, 0.179, 58.318), "700": (0.555, 0.163, 48.998), "800": (0.473, 0.137, 46.201), "900": (0.414, 0.112, 45.904), "950": (0.279, 0.077, 45.635)},
    "yellow": {"50": (0.987, 0.026, 102.212), "100": (0.973, 0.071, 103.193), "200": (0.945, 0.129, 101.54), "300": (0.905, 0.182, 98.111), "400": (0.852, 0.199, 91.936), "500": (0.795, 0.184, 86.047), "600": (0.681, 0.162, 75.834), "700": (0.554, 0.135, 66.442), "800": (0.476, 0.114, 61.907), "900": (0.421, 0.095, 57.708), "950": (0.286, 0.066, 53.813)},
    "lime": {"50": (0.986, 0.031, 120.757), "100": (0.967, 0.067, 122.328), "200": (0.938, 0.127, 124.321), "300": (0.897, 0.196, 126.665), "400": (0.841, 0.238, 128.85), "500": (0.768, 0.233, 130.85), "600": (0.648, 0.2, 131.684), "700": (0.532, 0.157, 131.589), "800": (0.453, 0.124, 130.933), "900": (0.405, 0.101, 131.063), "950": (0.274, 0.072, 132.109)},
    "green": {"50": (0.982, 0.018, 155.826), "100": (0.962, 0.044, 156.743), "200": (0.925, 0.084, 155.995), "300": (0.871, 0.15, 154.449), "400": (0.792, 0.209, 151.711), "500": (0.723, 0.219, 149.579), "600": (0.627, 0.194, 149.214), "700": (0.527, 0.154, 150.069), "800": (0.448, 0.119, 151.328), "900": (0.393, 0.095, 152.535), "950": (0.266, 0.065, 152.934)},
    "emerald": {"50": (0.979, 0.021, 166.113), "100": (0.95, 0.052, 163.051), "200": (0.905, 0.093, 164.15), "300": (0.845, 0.143, 164.978), "400": (0.765, 0.177, 163.223), "500": (0.696, 0.17, 162.48), "600": (0.596, 0.145, 163.225), "700": (0.508, 0.118, 165.612), "800": (0.432, 0.095, 166.913), "900": (0.378, 0.077, 168.94), "950": (0.262, 0.051, 172.552)},
    "cyan": {"50": (0.984, 0.019, 200.873), "100": (0.956, 0.045, 203.388), "200": (0.917, 0.08, 205.041), "300": (0.865, 0.127, 207.078), "400": (0.789, 0.154, 211.53), "500": (0.715, 0.143, 215.221), "600": (0.609, 0.126, 221.723), "700": (0.52, 0.105, 223.128), "800": (0.45, 0.085, 224.283), "900": (0.398, 0.07, 227.392), "950": (0.302, 0.056, 229.695)},
    "sky": {"50": (0.977, 0.013, 236.62), "100": (0.951, 0.026, 236.824), "200": (0.901, 0.058, 230.902), "300": (0.828, 0.111, 230.318), "400": (0.746, 0.16, 232.661), "500": (0.685, 0.169, 237.323), "600": (0.588, 0.158, 241.966), "700": (0.5, 0.134, 242.749), "800": (0.443, 0.11, 240.79), "900": (0.391, 0.09, 240.876), "950": (0.293, 0.066, 243.157)},
    "blue": {"50": (0.97, 0.014, 254.604), "100": (0.932, 0.032, 255.585), "200": (0.882, 0.059, 254.128), "300": (0.809, 0.105, 251.813), "400": (0.707, 0.165, 254.624), "500": (0.623, 0.214, 259.815), "600": (0.546, 0.245, 262.881), "700": (0.488, 0.243, 264.376), "800": (0.424, 0.199, 265.638), "900": (0.379, 0.146, 265.522), "950": (0.282, 0.091, 267.935)},
    "violet": {"50": (0.969, 0.016, 293.756), "100": (0.943, 0.029, 294.588), "200": (0.894, 0.057, 293.283), "300": (0.811, 0.111, 293.571), "400": (0.702, 0.183, 293.541), "500": (0.606, 0.25, 292.717), "600": (0.541, 0.281, 293.009), "700": (0.491, 0.27, 292.581), "800": (0.432, 0.232, 292.759), "900": (0.38, 0.189, 293.745), "950": (0.283, 0.141, 291.089)},
    "fuchsia": {"50": (0.977, 0.017, 320.058), "100": (0.952, 0.037, 318.852), "200": (0.903, 0.076, 319.62), "300": (0.833, 0.145, 321.434), "400": (0.74, 0.238, 322.16), "500": (0.667, 0.295, 322.15), "600": (0.591, 0.293, 322.896), "700": (0.518, 0.253, 323.949), "800": (0.452, 0.211, 324.591), "900": (0.401, 0.17, 325.612), "950": (0.293, 0.136, 325.661)},
    "pink": {"50": (0.971, 0.014, 343.198), "100": (0.948, 0.028, 342.258), "200": (0.899, 0.061, 343.231), "300": (0.823, 0.12, 346.018), "400": (0.718, 0.202, 349.761), "500": (0.656, 0.241, 354.308), "600": (0.592, 0.249, 0.584), "700": (0.525, 0.223, 3.958), "800": (0.459, 0.187, 3.815), "900": (0.408, 0.153, 2.432), "950": (0.284, 0.109, 3.907)}
}
# Kozu family: (Tailwind family, hue offset in degrees, light fill step, note)
MAP = {
    "Vermilion": ("red", 2, "600", "tomato red"), "Tangerine": ("orange", 2, "500", "clear orange"),
    "Saffron": ("yellow", -2, "500", "golden yellow"), "Citron": ("lime", -2, "500", "lemon-lime"),
    "Fern": ("green", -2, "500", "leaf green"), "Jade": ("emerald", 2, "500", "sea green"),
    "Lagoon": ("cyan", -4, "500", "aqua"), "Azure": ("sky", 2, "600", "clear cerulean"),
    "Cobalt": ("blue", 3, "600", "ultramarine blue"), "Iris": ("violet", -2, "600", "blue violet"),
    "Orchid": ("fuchsia", -2, "600", "purple magenta"), "Berry": ("pink", -4, "600", "raspberry pink"),
}
STATUS = {"Success": ("green", "600"), "Warning": ("amber", "500"), "Danger": ("red", "600"), "Info": ("sky", "600")}
NEUTRAL = {"name": "Graphite", "hue": 272.0, "steps": {"50": {"hex": "#F6F7FA", "oklch": [0.9766, 0.004, 272.0]}, "100": {"hex": "#EDEEF2", "oklch": [0.9493, 0.005, 272.0]}, "200": {"hex": "#DBDDE1", "oklch": [0.8972, 0.006, 272.0]}, "300": {"hex": "#C0C2C8", "oklch": [0.8144, 0.008, 272.0]}, "400": {"hex": "#A3A5AC", "oklch": [0.7236, 0.01, 272.0]}, "500": {"hex": "#8C8F96", "oklch": [0.649, 0.011, 272.0]}, "600": {"hex": "#70737A", "oklch": [0.5553, 0.012, 272.0]}, "700": {"hex": "#5A5C63", "oklch": [0.4746, 0.012, 272.0]}, "800": {"hex": "#43454B", "oklch": [0.3903, 0.011, 272.0]}, "900": {"hex": "#303238", "oklch": [0.3178, 0.01, 272.0]}, "950": {"hex": "#202126", "oklch": [0.2502, 0.008, 272.0]}}, "named": {"white": "#FFFFFF", "canvas": "#FCFCFC", "ink": "#0F1012", "night": "#0A0B0D", "nightContainer": "#151619", "nightRaised": "#1F2024", "nightInput": "#242529", "paper": "#F5F6F8"}}
STEPS = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950"]
INK, WHITE, CANVAS = "#0F1012", "#FFFFFF", "#FCFCFC"
NIGHT = NEUTRAL["named"]["night"]


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def oklch_to_linear(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_, m_, s_ = L + 0.3963377774 * a + 0.2158037573 * b, L - 0.1055613458 * a - 0.0638541728 * b, L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def in_gamut(rgb):
    return all(-1e-6 <= c <= 1 + 1e-6 for c in rgb)


def max_chroma(L, h):
    lo, hi = 0.0, 0.5
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if in_gamut(oklch_to_linear(L, mid, h)) else (lo, mid)
    return lo


def to_hex(L, C, h):
    C = min(C, max_chroma(L, h))
    rgb = oklch_to_linear(L, C, h)
    return "#" + "".join("%02X" % round(min(1, max(0, _gam(min(1, max(0, c))))) * 255) for c in rgb), C


def lum(hx):
    r, g, b = (_lin(int(hx[i:i + 2], 16) / 255) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    x, y = lum(a), lum(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


def ramp(base, offset):
    out = {}
    for s in STEPS:
        L, C, h = TAILWIND_V4[base][s]
        hx, c = to_hex(L, C, (h + offset) % 360)
        out[s] = {"hex": hx, "oklch": [L, round(c, 4), round((h + offset) % 360, 2)]}
    return out


def nudge(steps, s, ok, darker):
    L, C, h = steps[s]["oklch"]
    while not ok(to_hex(L, C, h)[0]):
        L += -0.004 if darker else 0.004
    hx, c = to_hex(L, C, h)
    steps[s] = {"hex": hx, "oklch": [round(L, 4), round(c, 4), h], "nudged": True}


def roles(steps, fill_step):
    st = lambda s: steps[s]["hex"]  # noqa: E731
    if int(fill_step) >= 600:
        if contrast(st(fill_step), WHITE) < 4.5:
            nudge(steps, fill_step, lambda hx: contrast(hx, WHITE) >= 4.55, True)
        on_fill = WHITE
    else:
        if contrast(st(fill_step), INK) < 4.5:
            nudge(steps, fill_step, lambda hx: contrast(hx, INK) >= 4.55, False)
        on_fill = INK
    tint, tint_dark = st("100"), st("900")
    text = next((s for s in ("600", "700", "800") if min(contrast(st(s), WHITE), contrast(st(s), CANVAS), contrast(st(s), tint)) >= 4.5), "800")
    dark = next(s for s in ("400", "300", "200") if min(contrast(st(s), NIGHT), contrast(st(s), tint_dark)) >= 4.5)
    link = "600" if min(contrast(st("600"), WHITE), contrast(st("600"), CANVAS)) >= 4.5 else text
    return {"fill": st(fill_step), "onFill": on_fill, "text": st(text), "link": st(link), "tint": tint,
            "fillDark": st(dark), "onFillDark": INK, "textDark": st(dark), "tintDark": tint_dark}, {"text": text, "textDark": dark}


def build():
    out = {"families": {}, "status": {}, "neutral": NEUTRAL}
    for name, (base, off, fill, note) in MAP.items():
        steps = ramp(base, off)
        r, used = roles(steps, fill)
        out["families"][name] = {"tailwind": base, "hueOffset": off, "fillStep": fill, "note": note, "roleSteps": used,
                                 "steps": steps, "roles": r}
    for name, (base, fill) in STATUS.items():
        steps = ramp(base, 0)
        r, _ = roles(steps, fill)
        fg = r["text"] if contrast(r["text"], steps["50"]["hex"]) >= 4.5 else steps["800"]["hex"]
        out["status"][name] = {"tailwind": base, "fillStep": fill, "steps": steps,
                               "roles": {"foreground": fg, "background": steps["50"]["hex"],
                                         "foregroundDark": r["textDark"], "backgroundDark": steps["950"]["hex"],
                                         "fill": r["fill"], "onFill": r["onFill"]}}
    return out


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
