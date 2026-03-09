from __future__ import annotations

from dataclasses import dataclass
from typing import List
import io

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image

from app.pipeline.pdf_to_images import PageImage


class ColorExtractionError(Exception):
    """主题色提取过程中发生的错误。"""


@dataclass
class StyleInfo:
    """与 Slide Schema 中 StyleInfo 对齐的颜色结构（子集）。"""

    primaryColor: str
    backgroundColor: str
    accentColors: List[str]


def _to_rgb_array(image_bytes: bytes) -> np.ndarray:
    """将 PNG bytes 转为 RGB numpy 数组。"""
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img = img.convert("RGB")
            return np.array(img)
    except Exception as exc:
        raise ColorExtractionError(f"Failed to decode image bytes: {exc}") from exc


def _rgb_to_hex(color: np.ndarray) -> str:
    r, g, b = [int(c) for c in color]
    return f"#{r:02X}{g:02X}{b:02X}"


def extract_colors(page_image: PageImage, k: int = 5, sample_size: int = 40000) -> StyleInfo:
    """
    使用 K-Means 从单页图片中提取背景色、主色和主题色。

    Args:
        page_image: PageImage 实例。
        k: K-Means 聚类数，默认 5。
        sample_size: 最大采样像素数，用于加速聚类。

    Returns:
        StyleInfo，包含 backgroundColor、primaryColor 和 accentColors（3–5 个）。

    Raises:
        ColorExtractionError: 当图像无法解析或聚类失败时抛出。
    """
    if k <= 0:
        raise ValueError("k must be positive.")

    try:
        with Image.open(io.BytesIO(page_image.image_bytes)) as img:
            img = img.convert("RGB")
            img_np = np.array(img)
    except Exception as exc:
        raise ColorExtractionError(f"Failed to decode image bytes: {exc}") from exc

    if img_np.size == 0:
        raise ColorExtractionError("Image array is empty.")

    pixels = img_np.reshape(-1, 3).astype(np.float32)

    # 灰度/单色图检测：颜色方差极小则直接返回单色方案
    if pixels.var() < 1e-3:
        single_hex = _rgb_to_hex(pixels.mean(axis=0))
        return StyleInfo(
            primaryColor=single_hex,
            backgroundColor=single_hex,
            accentColors=[single_hex],
        )

    if pixels.shape[0] > sample_size:
        indices = np.random.choice(pixels.shape[0], sample_size, replace=False)
        sample = pixels[indices]
    else:
        sample = pixels

    try:
        kmeans = KMeans(n_clusters=min(k, len(sample)), n_init=5, random_state=42)
        labels = kmeans.fit_predict(sample)
        centers = kmeans.cluster_centers_
    except Exception as exc:
        raise ColorExtractionError(f"KMeans clustering failed: {exc}") from exc

    # 统计每个聚类的像素占比
    counts = np.bincount(labels, minlength=len(centers))
    proportions = counts / counts.sum()

    # 计算每个中心的亮度（简单使用平均值）
    brightness = centers.mean(axis=1)

    # 背景色：占比最高的聚类中心
    bg_idx = int(np.argmax(proportions))
    background = centers[bg_idx]

    # 其余作为前景/主题候选，按亮度差和占比排序
    fg_indices = [i for i in range(len(centers)) if i != bg_idx]
    fg_sorted = sorted(
        fg_indices,
        key=lambda i: (-proportions[i], abs(brightness[i] - brightness[bg_idx])),
    )

    # 主色：第一个前景聚类（若不存在则回退到背景）
    primary_idx = fg_sorted[0] if fg_sorted else bg_idx
    primary = centers[primary_idx]

    # 主题色：按排序取前 3–5 个（若数量不足则去重后少量返回）
    accent_colors: List[str] = []
    for i in fg_sorted:
        hex_color = _rgb_to_hex(centers[i])
        if hex_color not in accent_colors:
            accent_colors.append(hex_color)
        if len(accent_colors) >= 5:
            break

    if not accent_colors:
        accent_colors = [_rgb_to_hex(primary)]

    # 确保至少 3 个 accentColors，若不足则用 primary/background 补齐
    while len(accent_colors) < 3:
        for extra in (_rgb_to_hex(primary), _rgb_to_hex(background)):
            if len(accent_colors) >= 3:
                break
            if extra not in accent_colors:
                accent_colors.append(extra)

    return StyleInfo(
        primaryColor=_rgb_to_hex(primary),
        backgroundColor=_rgb_to_hex(background),
        accentColors=accent_colors[:5],
    )

