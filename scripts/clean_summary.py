#!/usr/bin/env python3
"""清理梗概文件：去重、按章节顺序排列、清理多余空行。

用法: python3 clean_summary.py <梗概文件路径>
"""
import re, sys, os

# 中文数字到阿拉伯数字的映射
CN_NUMS = {
    '一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,
    '十一':11,'十二':12,'十三':13,'十四':14,'十五':15,'十六':16,'十七':17,
    '十八':18,'十九':19,'二十':20,'二十一':21,'二十二':22,'二十三':23,'二十四':24,
    '二十五':25,'二十六':26,'二十七':27,'二十八':28,'二十九':29,'三十':30,
    '三十一':31,'三十二':32,'三十三':33,'三十四':34,'三十五':35,
}

def cn_to_num(cn):
    return CN_NUMS.get(cn, 0)

def clean_summary(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按分段标题拆分
    pattern = r'(={10,}\s*第[一二三四五六七八九十百千]+部分：.*?={10,})'
    parts = re.split(pattern, content)

    header = parts[0].strip()  # 文件头部（标题等）

    # 解析每个分段，按部分编号去重（保留最长版本）
    sections = {}
    i = 1
    while i < len(parts):
        hdr = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""

        m = re.search(r'第([一二三四五六七八九十百千]+)部分', hdr)
        if m:
            num = cn_to_num(m.group(1))
            if num > 0:
                if num not in sections or len(body) > len(sections[num][1]):
                    sections[num] = (hdr, body)
        i += 2

    # 按顺序重建文件
    output = header + "\n\n"
    for num in sorted(sections.keys()):
        hdr, body = sections[num]
        output += hdr + "\n" + body

    # 清理多余空行（最多保留2个连续空行）
    output = re.sub(r'\n{4,}', '\n\n\n', output)
    output = output.strip() + "\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"清理完成: {os.path.basename(filepath)}")
    print(f"  唯一分段数: {len(sections)}")
    print(f"  总行数: {output.count(chr(10))}")
    print(f"  文件大小: {os.path.getsize(filepath) / 1024:.0f} KB")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 clean_summary.py <梗概文件路径> [更多文件...]")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        if os.path.exists(filepath):
            clean_summary(filepath)
        else:
            print(f"文件不存在: {filepath}")

if __name__ == '__main__':
    main()
