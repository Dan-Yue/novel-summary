#!/usr/bin/env python3
"""分析小说文件结构，检测章节标记并生成分段方案。

用法: python3 detect_chapters.py <小说文件路径> [--target-chunks 25]
"""
import re, os, sys, json

# 常见章节标记模式（按优先级排列）
CHAPTER_PATTERNS = [
    (r'^第[一二三四五六七八九十百千万零〇\d]+[章节回卷集部篇]', "中文数字+章节"),
    (r'^第\d+章', "阿拉伯数字+章"),
    (r'^第.{1,10}章', "通配+章"),
    (r'^Chapter\s+\d+', "英文Chapter"),
    (r'^\d+\.\s', "数字+点"),
]

def detect_chapters(filepath):
    """检测文件中的章节位置，返回 (行号列表, 使用的模式描述)。"""
    for pattern_str, desc in CHAPTER_PATTERNS:
        pattern = re.compile(pattern_str)
        chapters = []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                if pattern.match(line.strip()):
                    chapters.append(i)
        if len(chapters) >= 10:  # 至少10个章节才认为是有效模式
            return chapters, desc
    return [], "未找到"

def make_chunks(chapters, total_lines, target_chunks=25):
    """将章节列表分成 target_chunks 个分段。"""
    n_chapters = len(chapters)
    if n_chapters == 0:
        return []

    chunk_size = max(1, n_chapters // target_chunks)
    n_chunks = (n_chapters + chunk_size - 1) // chunk_size

    chunks = []
    idx = 0
    for i in range(n_chunks):
        start_ch = idx
        end_ch = min(idx + chunk_size - 1, n_chapters - 1)
        start_line = chapters[start_ch]
        end_line = chapters[end_ch + 1] - 1 if end_ch + 1 < n_chapters else total_lines
        chunks.append({
            "chunk_id": i,
            "start_chapter": start_ch + 1,
            "end_chapter": end_ch + 1,
            "chapter_count": end_ch - start_ch + 1,
            "start_line": start_line,
            "end_line": end_line,
        })
        idx += chunk_size

    return chunks

def main():
    if len(sys.argv) < 2:
        print("用法: python3 detect_chapters.py <小说文件路径> [--target-chunks N]")
        sys.exit(1)

    filepath = sys.argv[1]
    target = 25
    if '--target-chunks' in sys.argv:
        idx = sys.argv.index('--target-chunks')
        target = int(sys.argv[idx + 1])

    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    file_size = os.path.getsize(filepath)
    total_lines = sum(1 for _ in open(filepath, 'r', encoding='utf-8', errors='ignore'))

    chapters, pattern_desc = detect_chapters(filepath)

    print(f"文件: {os.path.basename(filepath)}")
    print(f"大小: {file_size / 1024 / 1024:.1f} MB")
    print(f"总行数: {total_lines}")
    print(f"章节模式: {pattern_desc}")
    print(f"检测到章节数: {len(chapters)}")

    if len(chapters) == 0:
        print("\n无法自动检测章节。请手动查找章节标记并指定行范围。")
        sys.exit(0)

    # 根据文件大小自动调整分段数
    if file_size < 2 * 1024 * 1024:  # < 2MB
        target = min(target, 5)
    elif file_size < 5 * 1024 * 1024:  # < 5MB
        target = min(target, 10)

    chunks = make_chunks(chapters, total_lines, target)

    print(f"\n分段方案: {len(chunks)} 段")
    print("-" * 70)
    for c in chunks:
        print(f"  段 {c['chunk_id']+1:2d}: 第{c['start_chapter']:4d}-{c['end_chapter']:4d}章 "
              f"({c['chapter_count']:3d}章) 行 {c['start_line']:7d}-{c['end_line']:7d}")

    # 输出 JSON 方案
    plan = {
        "file": filepath,
        "file_size_mb": round(file_size / 1024 / 1024, 1),
        "total_lines": total_lines,
        "total_chapters": len(chapters),
        "pattern": pattern_desc,
        "chunks": chunks,
    }
    plan_path = filepath.rsplit('.', 1)[0] + '_chapters.json'
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"\n分段方案已保存到: {plan_path}")

if __name__ == '__main__':
    main()
