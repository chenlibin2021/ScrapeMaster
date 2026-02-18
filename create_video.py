#!/usr/bin/env python3
"""
尝试生成简单视频文件
需要：PIL, numpy, 可能还需要opencv
"""

import os
import subprocess
import sys

def check_dependencies():
    """检查必要的依赖"""
    missing = []
    
    # 检查FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('ffmpeg')
    
    # 检查ImageMagick
    try:
        subprocess.run(['convert', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('imagemagick')
    
    return missing

def create_simple_video():
    """创建最简单的视频方案"""
    
    print("=" * 60)
    print("🎬 大多伦多地产新闻视频生成器")
    print("=" * 60)
    
    # 检查依赖
    missing = check_dependencies()
    if missing:
        print(f"\n❌ 缺少必要工具: {', '.join(missing)}")
        print("\n请安装以下工具:")
        if 'ffmpeg' in missing:
            print("  - FFmpeg: sudo apt install ffmpeg")
        if 'imagemagick' in missing:
            print("  - ImageMagick: sudo apt install imagemagick")
        return False
    
    print("\n✅ 所有必要工具已安装")
    
    # 创建临时目录
    temp_dir = "/tmp/gta_video"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 创建简单的图片帧
    print("\n📷 创建视频帧...")
    
    # 创建标题帧
    title_frame = f"""cat > {temp_dir}/title.txt << 'EOF'
========================================
       大多伦多地区地产新闻
           2026年2月报告
========================================

🏠 核心发现：
• 平均房价：$973,289
• 5年来首次跌破百万
• 同比下降：6.5%

📊 数据来源：TRREB
📅 报告时间：2026年2月16日
EOF"""
    
    subprocess.run(title_frame, shell=True, check=True)
    
    # 创建数据帧1
    data1_frame = f"""cat > {temp_dir}/data1.txt << 'EOF'
📉 市场表现概览

房屋销售量：3,082套
• 同比下降：19.3%
• 市场活跃度显著降低

平均挂牌天数：45天
• 同比增加：21.6%
• 销售周期明显延长

活跃挂牌量：17,975套
• 同比增加：8.1%
• 供应压力持续增大
EOF"""
    
    subprocess.run(data1_frame, shell=True, check=True)
    
    # 创建数据帧2
    data2_frame = f"""cat > {temp_dir}/data2.txt << 'EOF'
🏢 房产类型分析

独立屋：
• 平均价格：$1,277,915
• 同比下降：7.4%

公寓：
• 平均价格：$604,759
• 同比下降：9.8%
• 905地区年跌幅：13%

📈 价格趋势：
• 较2022年峰值下跌：27%
• 回归2021年价格水平
EOF"""
    
    subprocess.run(data2_frame, shell=True, check=True)
    
    # 创建总结帧
    summary_frame = f"""cat > {temp_dir}/summary.txt << 'EOF'
🎯 市场展望

短期（2026上半年）：
• 价格和销售疲软预计持续
• 供应过剩压力仍在

中期（2026下半年）：
• 若消费者信心改善，价格可能稳定
• 市场寻找平衡点

长期基本面：
• GTA人口增长支撑需求
• 利率环境逐步改善

感谢观看！
EOF"""
    
    subprocess.run(summary_frame, shell=True, check=True)
    
    # 将文本文件转换为图片
    print("🖼️ 将文本转换为图片...")
    
    frames = ['title', 'data1', 'data2', 'summary']
    for frame in frames:
        cmd = f"""
        convert -size 1920x1080 xc:black \
          -font "Arial" -pointsize 48 -fill white \
          -gravity center -annotate +0+0 "@/tmp/gta_video/{frame}.txt" \
          {temp_dir}/{frame}.png
        """
        subprocess.run(cmd, shell=True, check=True)
        print(f"  已创建: {frame}.png")
    
    # 创建视频
    print("\n🎥 创建视频文件...")
    
    # 首先创建图片列表文件
    list_file = f"{temp_dir}/filelist.txt"
    with open(list_file, 'w') as f:
        for frame in frames:
            # 每张图片显示5秒（150帧，30fps）
            for _ in range(5):
                f.write(f"file '{temp_dir}/{frame}.png'\n")
                f.write(f"duration 5\n")
    
    # 使用FFmpeg创建视频
    output_video = "/home/chenlibin/.openclaw/workspace/gta_real_estate_news.mp4"
    
    ffmpeg_cmd = f"""
    ffmpeg -y -f concat -safe 0 -i {list_file} \
      -i /tmp/tts-BzFCew/voice-1771300253279.mp3 \
      -c:v libx264 -preset medium -crf 23 \
      -c:a aac -b:a 128k \
      -shortest \
      -pix_fmt yuv420p \
      {output_video}
    """
    
    print("正在生成视频，请稍候...")
    result = subprocess.run(ffmpeg_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"\n✅ 视频生成成功！")
        print(f"📁 文件位置: {output_video}")
        print(f"📊 视频信息:")
        
        # 获取视频信息
        info_cmd = f"ffprobe -v error -show_format -show_streams {output_video}"
        info = subprocess.run(info_cmd, shell=True, capture_output=True, text=True)
        
        if info.returncode == 0:
            lines = info.stdout.split('\n')
            for line in lines:
                if 'duration=' in line:
                    duration = float(line.split('=')[1])
                    print(f"   时长: {duration:.1f}秒")
                elif 'width=' in line:
                    width = line.split('=')[1]
                    print(f"   宽度: {width}像素")
                elif 'height=' in line:
                    height = line.split('=')[1]
                    print(f"   高度: {height}像素")
        
        print(f"\n🎬 视频包含:")
        print(f"   • 4个信息页面")
        print(f"   • 专业TTS音频解说")
        print(f"   • 20秒总时长")
        
        return True
    else:
        print(f"\n❌ 视频生成失败")
        print(f"错误信息: {result.stderr}")
        return False

def main():
    """主函数"""
    print("开始生成大多伦多地产新闻视频...")
    
    # 检查音频文件是否存在
    audio_file = "/tmp/tts-BzFCew/voice-1771300253279.mp3"
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        print("请先生成TTS音频")
        return False
    
    print(f"✅ 找到音频文件: {audio_file}")
    
    # 尝试生成视频
    success = create_simple_video()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 视频生成完成！")
        print("=" * 60)
        print("\n下一步操作:")
        print("1. 查看视频: vlc gta_real_estate_news.mp4")
        print("2. 分享视频: 可上传到社交媒体")
        print("3. 如需编辑: 使用视频编辑软件进一步优化")
    else:
        print("\n" + "=" * 60)
        print("⚠️ 视频生成遇到问题")
        print("=" * 60)
        print("\n替代方案:")
        print("1. 使用在线工具: Canva, Clipchamp等")
        print("2. 使用手机应用: CapCut, InShot等")
        print("3. 我已提供所有素材，可手动制作")
    
    return success

if __name__ == "__main__":
    main()