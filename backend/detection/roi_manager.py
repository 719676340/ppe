# backend/detection/roi_manager.py
import json
import cv2
import numpy as np
from typing import List, Dict, Tuple

class ROIManager:
    """ROI (感兴趣区域) 管理器"""

    @staticmethod
    def parse_coordinates(coordinates_json: str) -> List[Tuple[float, float]]:
        """
        解析ROI坐标字符串

        Args:
            coordinates_json: JSON格式的坐标字符串

        Returns:
            归一化坐标列表 [(x1, y1), (x2, y2), ...]
        """
        try:
            coords = json.loads(coordinates_json)
            return [(float(x), float(y)) for x, y in coords]
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            raise ValueError(f"无效的坐标格式: {e}")

    @staticmethod
    def scale_coordinates(
        normalized_coords: List[Tuple[float, float]],
        image_width: int,
        image_height: int
    ) -> List[Tuple[int, int]]:
        """
        将归一化坐标转换为实际像素坐标

        Args:
            normalized_coords: 归一化坐标 [(x1, y1), ...] 范围0-1
            image_width: 图像宽度
            image_height: 图像高度

        Returns:
            实际像素坐标 [(x1, y1), ...]
        """
        result = []
        for x, y in normalized_coords:
            # 如果坐标在0-1范围内，认为是归一化坐标，需要缩放
            if 0 <= x <= 1 and 0 <= y <= 1:
                px = int(x * image_width)
                py = int(y * image_height)
            else:
                # 否则认为是像素坐标，直接使用
                px = int(x)
                py = int(y)
            result.append((px, py))

        return result

    @staticmethod
    def point_in_polygon(
        point: Tuple[float, float],
        polygon: List[Tuple[float, float]]
    ) -> bool:
        """
        判断点是否在多边形内 (射线法)

        Args:
            point: 待判断点 (x, y)
            polygon: 多边形顶点列表 [(x1, y1), (x2, y2), ...]

        Returns:
            True表示在多边形内，False表示在多边形外
        """
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def is_bbox_in_zone(
        self,
        bbox: List[float],
        zone_coords: List[Tuple[float, float]]
    ) -> bool:
        """
        判断边界框中心点是否在检测区域内

        Args:
            bbox: 边界框 [x1, y1, x2, y2]
            zone_coords: 区域顶点坐标列表 [(x1, y1), ...]

        Returns:
            True表示在区域内，False表示在区域外
        """
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        return self.point_in_polygon((center_x, center_y), zone_coords)

    def draw_zone(
        self,
        image: np.ndarray,
        zone_coords: List[Tuple[int, int]],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        在图像上绘制检测区域

        Args:
            image: OpenCV图像
            zone_coords: 区域顶点坐标列表
            color: 颜色 (B, G, R)
            thickness: 线条粗细

        Returns:
            绘制后的图像
        """
        image_copy = image.copy()
        if len(zone_coords) >= 3:
            pts = np.array(zone_coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(image_copy, [pts], True, color, thickness)
        return image_copy
