"""图标裁剪 crop_imageblocks 单元测试。"""
from __future__ import annotations

from app.pipeline.layout_ocr_models import Box2D, ImageBlock
from app.pipeline.icon_cropping import CroppedImage, crop_imageblocks
from app.pipeline.pdf_to_images import PageImage


def test_crop_imageblocks_returns_same_length_as_blocks(
    sample_page_image: PageImage,
) -> None:
    """返回列表长度应与 image_blocks 一致。"""
    blocks = [
        ImageBlock(
            id="img-1",
            resourceType="id",
            resource="img-1",
            box=Box2D(x=0.1, y=0.1, w=0.3, h=0.3),
        ),
    ]
    result = crop_imageblocks(sample_page_image, blocks)
    assert len(result) == 1
    assert result[0] is not None
    assert isinstance(result[0], CroppedImage)
    assert result[0].block_id == "img-1"
    assert result[0].page_number == sample_page_image.page_number
    assert len(result[0].image_bytes) > 0


def test_crop_imageblocks_empty_blocks(sample_page_image: PageImage) -> None:
    """空 blocks 应返回空列表。"""
    result = crop_imageblocks(sample_page_image, [])
    assert result == []


def test_crop_imageblocks_invalid_bbox_returns_none(
    sample_page_image: PageImage,
) -> None:
    """越界或零面积 bbox 对应位置可为 None。"""
    blocks = [
        ImageBlock(
            id="bad",
            resourceType="id",
            resource="bad",
            box=Box2D(x=0, y=0, w=0, h=0),
        ),
    ]
    result = crop_imageblocks(sample_page_image, blocks)
    assert len(result) == 1
    assert result[0] is None
