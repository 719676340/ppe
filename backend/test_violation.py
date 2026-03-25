#!/usr/bin/env python
"""测试违规记录功能"""
import sys
import os
import numpy as np
from pathlib import Path

# 添加backend目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from detection.detector import PPEDetector
from detection.violation_recorder import ViolationRecorder
from management.database import SessionLocal, Violation

def test_violation_recording():
    """测试违规记录"""
    print("=== 开始测试违规记录 ===")

    # 1. 初始化检测器
    print("\n1. 初始化检测器...")
    try:
        detector = PPEDetector()
        print(f"   ✓ 检测器初始化成功")
        print(f"   - 违规类别ID: {detector.violation_class_id}")
        print(f"   - 类别名称: {detector.class_names}")
    except Exception as e:
        print(f"   ✗ 检测器初始化失败: {e}")
        return False

    # 2. 初始化违规记录器
    print("\n2. 初始化违规记录器...")
    try:
        recorder = ViolationRecorder('./static/uploads')
        print(f"   ✓ 违规记录器初始化成功")
    except Exception as e:
        print(f"   ✗ 违规记录器初始化失败: {e}")
        return False

    # 3. 创建测试帧和检测结果
    print("\n3. 创建测试数据...")
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # 测试两种情况
    test_cases = [
        {
            'name': '违规检测 (no_ppe)',
            'detection': {
                'bbox': [100, 100, 200, 200],
                'confidence': 0.9,
                'class_id': 0,  # no_ppe - 违规
                'class_name': 'no_ppe',
                'is_compliant': False,
                'is_violation': True
            }
        },
        {
            'name': '正常检测 (with_ppe)',
            'detection': {
                'bbox': [300, 100, 400, 200],
                'confidence': 0.85,
                'class_id': 1,  # with_ppe - 正常
                'class_name': 'with_ppe',
                'is_compliant': True,
                'is_violation': False
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n4.{i} 测试: {test_case['name']}")
        detection = test_case['detection']
        print(f"   - class_id: {detection['class_id']}")
        print(f"   - is_violation: {detection['is_violation']}")

        # 清空去重缓存
        recorder.clear_cache()

        # 调用违规记录器
        if detection['is_violation']:
            print(f"   - 调用违规记录器...")
            recorder.record_violation(
                camera_id=1,
                zone_id=1,
                frame=test_frame,
                detection=detection
            )

    # 5. 检查数据库
    print("\n5. 检查数据库...")
    db = SessionLocal()
    try:
        count = db.query(Violation).count()
        print(f"   - 数据库中违规记录数: {count}")

        if count > 0:
            violations = db.query(Violation).all()
            for v in violations:
                print(f"   - 记录 {v.id}: camera_id={v.camera_id}, zone_id={v.zone_id}, time={v.violation_time}")
        else:
            print(f"   ✗ 没有违规记录被保存")
    finally:
        db.close()

    # 6. 检查uploads目录
    print("\n6. 检查uploads目录...")
    upload_dir = Path('./static/uploads')
    if upload_dir.exists():
        files = list(upload_dir.glob('violation_*.jpg'))
        print(f"   - uploads目录中有 {len(files)} 个违规截图文件")
        if files:
            for f in files:
                print(f"     - {f.name}")
    else:
        print(f"   ✗ uploads目录不存在")

    print("\n=== 测试完成 ===")
    return True

if __name__ == "__main__":
    test_violation_recording()
