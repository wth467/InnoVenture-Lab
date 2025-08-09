import argparse
import cv2
import os
from core import DCTWatermark
from tests.robustness import simple_robustness_test

def main():
    parser = argparse.ArgumentParser(description="数字水印鲁棒性测试工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 测试命令
    test_parser = subparsers.add_parser('test', help='运行鲁棒性测试')
    test_parser.add_argument('image', help='测试图像路径')
    test_parser.add_argument('watermark', help='水印图像路径')
    test_parser.add_argument('--attacks', nargs='+', default=None, 
                            help='攻击类型列表 (默认: 常见攻击)')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        simple_robustness_test(args.image, args.watermark, args.attacks)

if __name__ == "__main__":
    main()