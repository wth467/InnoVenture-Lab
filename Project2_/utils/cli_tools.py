import argparse
import cv2
from core import DCTWatermark

def main():
    parser = argparse.ArgumentParser(description="数字水印嵌入与提取工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 嵌入命令
    embed_parser = subparsers.add_parser('embed', help='嵌入水印')
    embed_parser.add_argument('input', help='输入图像路径')
    embed_parser.add_argument('watermark', help='水印图像路径')
    embed_parser.add_argument('output', help='输出图像路径')
    embed_parser.add_argument('--alpha', type=float, default=0.05, help='水印强度')
    embed_parser.add_argument('--password', type=int, default=0, help='随机种子')
    
    # 提取命令
    extract_parser = subparsers.add_parser('extract', help='提取水印')
    extract_parser.add_argument('input', help='含水印图像路径')
    extract_parser.add_argument('wm_shape', nargs=2, type=int, help='水印形状 (高 宽)')
    extract_parser.add_argument('output', help='提取的水印输出路径')
    extract_parser.add_argument('--password', type=int, default=0, help='随机种子')
    
    args = parser.parse_args()
    
    if args.command == 'embed':
        img = cv2.imread(args.input)
        wm = cv2.imread(args.watermark, cv2.IMREAD_GRAYSCALE)
        
        watermarker = DCTWatermark(
            password=args.password,
            alpha=args.alpha
        )
        result = watermarker.embed(img, wm)
        cv2.imwrite(args.output, result)
        print(f"水印嵌入成功，保存至 {args.output}")
    
    elif args.command == 'extract':
        img = cv2.imread(args.input)
        watermarker = DCTWatermark(password=args.password)
        extracted = watermarker.extract(img, tuple(args.wm_shape))
        cv2.imwrite(args.output, extracted)
        print(f"水印提取成功，保存至 {args.output}")

if __name__ == "__main__":
    main()