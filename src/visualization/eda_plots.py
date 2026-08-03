"""Dependency-light SVG plotting utilities for reproducible EDA reporting."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Sequence

import numpy as np


PALETTE = {"navy": "#12355B", "blue": "#1F6AA5", "teal": "#008C95", "red": "#B33A3A", "grey": "#5C6770", "light": "#E8EEF3"}


def _write(path: str | Path, body: str, width: int = 1200, height: int = 700) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        '<style>text{font-family:Arial,sans-serif;fill:#17212B}.title{font-size:25px;font-weight:700}.sub{font-size:14px;fill:#5C6770}.axis{font-size:12px;fill:#5C6770}.label{font-size:13px}.value{font-size:12px;font-weight:700}</style>'
        + body + '</svg>', encoding="utf-8"
    )


def bar_chart(path: str | Path, labels: Sequence[str], values: Sequence[float], title: str, *, subtitle: str = "", value_format: str = ".1f", color: str = PALETTE["blue"], horizontal: bool = True) -> None:
    """Save a legible single-series bar chart as an SVG."""
    labels, values = list(labels), list(values)
    width, height, left, top, bottom = 1200, max(440, 100 + 35 * len(labels)), 285 if horizontal else 75, 80, 65
    maximum = max(values) if values and max(values) > 0 else 1.0
    body = f'<text x="40" y="38" class="title">{escape(title)}</text><text x="40" y="62" class="sub">{escape(subtitle)}</text>'
    if horizontal:
        plot_width = width - left - 100
        for i, (label, value) in enumerate(zip(labels, values)):
            y = top + i * 35
            bar_width = (value / maximum) * plot_width
            body += f'<text x="{left-10}" y="{y+19}" text-anchor="end" class="label">{escape(str(label))}</text>'
            body += f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="23" fill="{color}" rx="2"/>'
            body += f'<text x="{left+bar_width+8:.1f}" y="{y+18}" class="value">{value:{value_format}}</text>'
    else:
        plot_height, plot_width = height - top - bottom, width - left - 70
        n = max(len(labels), 1); bar_w = plot_width / n * 0.7
        for i, (label, value) in enumerate(zip(labels, values)):
            x = left + i * plot_width / n + (plot_width/n-bar_w)/2
            bar_h = value / maximum * plot_height; y = top + plot_height - bar_h
            body += f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}"/>'
            body += f'<text x="{x+bar_w/2:.1f}" y="{top+plot_height+18}" text-anchor="end" transform="rotate(-45 {x+bar_w/2:.1f} {top+plot_height+18})" class="axis">{escape(str(label))}</text>'
    _write(path, body, width, height)


def line_chart(path: str | Path, labels: Sequence[str], series: dict[str, Sequence[float]], title: str, *, subtitle: str = "", y_label: str = "") -> None:
    """Save a multi-series line chart as an SVG."""
    width, height, left, top, right, bottom = 1200, 640, 90, 90, 230, 95
    all_values = [v for values in series.values() for v in values]
    lo, hi = min(all_values, default=0), max(all_values, default=1)
    if hi == lo: hi = lo + 1
    body = f'<text x="40" y="38" class="title">{escape(title)}</text><text x="40" y="62" class="sub">{escape(subtitle)}</text>'
    body += f'<text x="20" y="{top+20}" class="axis">{escape(y_label)}</text>'
    pw, ph = width-left-right, height-top-bottom
    for step in range(6):
        value = lo + (hi-lo)*step/5; y = top+ph-ph*step/5
        body += f'<line x1="{left}" y1="{y:.1f}" x2="{left+pw}" y2="{y:.1f}" stroke="#E8EEF3"/>'
        body += f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" class="axis">{value:.2f}</text>'
    colors = [PALETTE['navy'], PALETTE['red'], PALETTE['teal'], PALETTE['blue']]
    n = max(len(labels)-1, 1)
    for j, (name, values) in enumerate(series.items()):
        points = []
        for i, value in enumerate(values):
            x = left+pw*i/n; y = top+ph-(value-lo)/(hi-lo)*ph; points.append(f'{x:.1f},{y:.1f}')
        color = colors[j % len(colors)]
        body += f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="3"/>'
        body += f'<text x="{left+pw+20}" y="{top+25+j*25}" class="label" fill="{color}">{escape(name)}</text>'
    for i, label in enumerate(labels):
        x = left+pw*i/n
        body += f'<text x="{x:.1f}" y="{top+ph+25}" text-anchor="end" transform="rotate(-35 {x:.1f} {top+ph+25})" class="axis">{escape(str(label))}</text>'
    _write(path, body, width, height)


def heatmap(path: str | Path, labels: Sequence[str], matrix: np.ndarray, title: str) -> None:
    """Save a correlation heatmap with numeric labels as an SVG."""
    labels = list(labels); n = len(labels); cell = max(55, min(95, 800 // max(n, 1))); left, top = 230, 120; width, height = left+n*cell+50, top+n*cell+80
    body = f'<text x="35" y="40" class="title">{escape(title)}</text><text x="35" y="65" class="sub">Correlation coefficients; red = positive, blue = negative.</text>'
    for i, row_label in enumerate(labels):
        body += f'<text x="{left-8}" y="{top+i*cell+cell*.62:.1f}" text-anchor="end" class="axis">{escape(row_label)}</text>'
        for j, value in enumerate(matrix[i]):
            v = float(np.nan_to_num(value)); intensity = int(220 - abs(v)*120)
            color = f'#{intensity:02x}{intensity:02x}{255 if v < 0 else intensity:02x}' if v < 0 else f'#ff{intensity:02x}{intensity:02x}'
            x,y = left+j*cell,top+i*cell
            body += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color}" stroke="#FFFFFF"/>'
            body += f'<text x="{x+cell/2}" y="{y+cell*.58:.1f}" text-anchor="middle" class="axis">{v:.2f}</text>'
    for j, col_label in enumerate(labels): body += f'<text x="{left+j*cell+cell/2}" y="{top-8}" text-anchor="end" transform="rotate(-45 {left+j*cell+cell/2} {top-8})" class="axis">{escape(col_label)}</text>'
    _write(path, body, width, height)


def histogram(path: str | Path, values: np.ndarray, title: str, *, x_label: str, bins: int = 30) -> None:
    """Save a histogram with a Gaussian-kernel density overlay as an SVG."""
    values = values[np.isfinite(values)]; counts, edges = np.histogram(values, bins=bins); width,height,left,top,bottom = 1200,640,95,80,90; pw,ph=width-left-50,height-top-bottom
    maximum=max(counts.max(),1); body=f'<text x="40" y="38" class="title">{escape(title)}</text><text x="40" y="62" class="sub">Distribution shown with Gaussian-kernel density overlay.</text>'
    for i,c in enumerate(counts):
        x=left+i*pw/bins; h=c/maximum*ph; body+=f'<rect x="{x:.1f}" y="{top+ph-h:.1f}" width="{pw/bins-1:.1f}" height="{h:.1f}" fill="#1F6AA5" opacity="0.75"/>'
    xs=np.linspace(edges[0],edges[-1],160); bw=max(np.std(values)*(len(values)**(-1/5)),1e-9); density=np.exp(-0.5*((xs[:,None]-values[::max(1,len(values)//3000)])/bw)**2).mean(axis=1)/(bw*2.5066); density=density/density.max()*ph
    pts=[]
    for x,d in zip(xs,density): pts.append(f'{left+(x-edges[0])/(edges[-1]-edges[0])*pw:.1f},{top+ph-d:.1f}')
    body+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="#B33A3A" stroke-width="3"/>'
    body+=f'<text x="{left+pw/2}" y="{height-20}" text-anchor="middle" class="label">{escape(x_label)}</text>'
    _write(path,body,width,height)
