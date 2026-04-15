import os
import shutil
import re
from datetime import datetime
import argparse

def classify_images_by_timestamp_range(source_folder, target_folder, start_timestamp=None, end_timestamp=None):
    """
    按时间戳范围分类图片文件
    
    参数:
    source_folder: 源文件夹路径，包含待分类的图片
    target_folder: 目标文件夹路径，分类后的图片将放在这里
    start_timestamp: 起始时间戳（包含），字符串或整数
    end_timestamp: 结束时间戳（包含），字符串或整数
    """
    
    # 创建目标文件夹
    keypoints_folder = os.path.join(target_folder, "Key points")  # 恢复Key points文件夹
    forwardview_folder = os.path.join(target_folder, "Forward-view")
    panoramicview_folder = os.path.join(target_folder, "Panoramic-view")
    other_folder = os.path.join(target_folder, "other")
    
    # 如果目标文件夹不存在，则创建
    os.makedirs(keypoints_folder, exist_ok=True)  # 恢复创建Key points文件夹
    os.makedirs(forwardview_folder, exist_ok=True)
    os.makedirs(panoramicview_folder, exist_ok=True)
    os.makedirs(other_folder, exist_ok=True)
    
    # 转换时间戳为整数（如果提供）
    start_ts = int(start_timestamp) if start_timestamp else None
    end_ts = int(end_timestamp) if end_timestamp else None
    
    print(f"筛选条件: {start_ts if start_ts else '无限制'} 到 {end_ts if end_ts else '无限制'}")
    
    # 正则表达式模式（重点修改：匹配以match结尾的文件名）
    match_pattern = r'^(\d+).*_match\.jpg$'  # 匹配 时间戳_任意内容_match.jpg
    input_pattern = r'^(\d+)_input\.jpg$'    # 匹配 时间戳_input.jpg
    camera_pattern = r'^(\d+)_camera_\d+\.jpg$'  # 匹配 时间戳_camera_数字.jpg（不含match）
    
    # 统计信息
    stats = {
        "keypoints": 0,        # 恢复keypoints统计
        "forwardview": 0,     
        "panoramicview": 0,   
        "other": 0,
        "skipped_by_time": 0,
        "total_processed": 0
    }
    
    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        # 只处理jpg文件
        if not filename.lower().endswith('.jpg'):
            continue
            
        stats["total_processed"] += 1
        source_path = os.path.join(source_folder, filename)
        
        # 提取时间戳并判断文件类型（优先级：match结尾 > input > camera > other）
        timestamp = None
        file_type = "other"
        
        # 1. 匹配以match结尾的文件（如1776069482223_camera_1_match.jpg）
        match = re.match(match_pattern, filename)
        if match:
            timestamp = int(match.group(1))
            file_type = "keypoints"
        else:
            # 2. 匹配input文件
            match = re.match(input_pattern, filename)
            if match:
                timestamp = int(match.group(1))
                file_type = "forwardview"
            else:
                # 3. 匹配camera文件（不含match）
                match = re.match(camera_pattern, filename)
                if match:
                    timestamp = int(match.group(1))
                    file_type = "panoramicview"
        
        # 检查时间戳范围
        in_time_range = True
        if timestamp:
            if start_ts and timestamp < start_ts:
                in_time_range = False
            if end_ts and timestamp > end_ts:
                in_time_range = False
        
        # 如果不在时间范围内，跳过
        if not in_time_range:
            stats["skipped_by_time"] += 1
            if timestamp:
                print(f"⏰ 跳过(时间范围外): {filename} (时间戳: {timestamp})")
            continue
        
        # 根据文件类型分类
        if file_type == "keypoints":
            dest_path = os.path.join(keypoints_folder, filename)
            print("复制到:",filename)
            shutil.copy2(source_path, dest_path)
            stats["keypoints"] += 1
            print(f"✅ 已分类(关键点): {filename} (时间戳: {timestamp})")
            
        elif file_type == "forwardview":
            dest_path = os.path.join(forwardview_folder, filename)
            print("复制到:",filename)
            shutil.copy2(source_path, dest_path)
            stats["forwardview"] += 1
            print(f"✅ 已分类(前视): {filename} (时间戳: {timestamp})")
            
        elif file_type == "panoramicview":
            dest_path = os.path.join(panoramicview_folder, filename)
            print("复制到:",filename)
            shutil.copy2(source_path, dest_path)
            stats["panoramicview"] += 1
            print(f"✅ 已分类(全景): {filename} (时间戳: {timestamp})")
            
        else:
            dest_path = os.path.join(other_folder, filename)
            print("复制到:",filename)
            shutil.copy2(source_path, dest_path)
            stats["other"] += 1
            print(f"❓ 无法分类: {filename}")
    
    # 打印统计信息
    print("\n" + "="*60)
    print("分类完成！统计信息：")
    print(f"总扫描文件数: {stats['total_processed']} 个")
    print(f"因时间范围跳过: {stats['skipped_by_time']} 个")
    print(f"关键点图片(Key points): {stats['keypoints']} 个")  # 恢复显示
    print(f"前视图片(Forward-view): {stats['forwardview']} 个")
    print(f"全景图片(Panoramic-view): {stats['panoramicview']} 个")
    print(f"其他文件(other): {stats['other']} 个")
    print(f"实际处理文件数: {stats['keypoints'] + stats['forwardview'] + stats['panoramicview'] + stats['other']} 个")
    print(f"结果已保存到: {target_folder}")
    
    # 显示文件夹映射关系
    print("\n" + "="*60)
    print("文件类型映射关系：")
    print("原始文件名模式                -> 分类文件夹")
    print("时间戳_任意内容_match.jpg    -> Key points")
    print("时间戳_input.jpg            -> Forward-view")
    print("时间戳_camera_数字.jpg       -> Panoramic-view")
    print("="*60)

def timestamp_to_datetime(timestamp):
    """将时间戳转换为可读的日期时间格式"""
    try:
        # 时间戳可能是毫秒级的，转换为秒
        if timestamp > 10**12:  # 如果是毫秒级时间戳
            dt = datetime.fromtimestamp(timestamp / 1000)
        else:  # 如果是秒级时间戳
            dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "无效时间戳"

def classify_with_time_range():
    """带时间范围筛选的命令行版本"""
    
    print("="*60)
    print("图片分类工具 - 按时间戳范围筛选")
    print("="*60)
    print("文件类型映射：")
    print("  *_match.jpg       -> Key points 文件夹")  # 更新提示
    print("  *_input.jpg       -> Forward-view 文件夹")
    print("  *_camera_*.jpg    -> Panoramic-view 文件夹 (不含match)")
    print("="*60)
    
    # 获取用户输入
    source_folder = input("请输入源文件夹路径: ").strip()
    if not os.path.exists(source_folder):
        print(f"错误: 文件夹 '{source_folder}' 不存在！")
        return
    
    target_folder = input("请输入目标文件夹路径: ").strip()
    
    # 时间范围筛选
    print("\n" + "-"*60)
    print("时间范围筛选 (可选)")
    print("提示: 时间戳通常为13位数字 (毫秒级时间戳)")
    print("例如: 1769483507029")
    print("-"*60)
    
    use_time_filter = input("是否按时间范围筛选? (y/n): ").strip().lower()
    
    start_timestamp = None
    end_timestamp = None
    
    if use_time_filter == 'y':
        start_input = input("请输入起始时间戳 (留空则不限制): ").strip()
        end_input = input("请输入结束时间戳 (留空则不限制): ").strip()
        
        if start_input:
            start_timestamp = start_input
            print(f"起始时间: {timestamp_to_datetime(int(start_input))}")
        
        if end_input:
            end_timestamp = end_input
            print(f"结束时间: {timestamp_to_datetime(int(end_input))}")
    
    print("\n开始分类...")
    print("-"*60)
    
    classify_images_by_timestamp_range(source_folder, target_folder, start_timestamp, end_timestamp)

    
def main():
    parser = argparse.ArgumentParser(description="图片分类工具")

    parser.add_argument("--src", required=True, help="源文件夹路径")
    parser.add_argument("--dst", required=True, help="目标文件夹路径")
    parser.add_argument("--start", help="起始时间戳", default=None)
    parser.add_argument("--end", help="结束时间戳", default=None)

    args = parser.parse_args()

    classify_images_by_timestamp_range(
        args.src,
        args.dst,
        args.start,
        args.end
    )

if __name__ == "__main__":
    main()
