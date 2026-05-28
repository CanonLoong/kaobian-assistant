# word_counter.py
# 功能：读取考编笔记，统计高频关键词，帮助抓住复习重点

import re
from collections import Counter

def read_notes(filename):
    """读取笔记文件"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def extract_words(text):
    """
    提取中文词语（2字以上）
    使用正则表达式匹配中文字符
    """
    # 匹配连续的中文字符（2个及以上）
    words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
    return words

def count_top_words(words, top_n=10):
    """
    统计词频，排除停用词，返回前N个
    """
    # 停用词：考编教材中常见但对抓重点无意义的词
    stop_words = {
        '一个', '可以', '这个', '进行', '使用', '通过', '需要', '作为',
        '方法', '数据', '系统', '模型', '包括', '采用', '具有', '基本',
        '步骤', '管理', '维护', '处理', '存储', '组成', '部分', '目前',
        '重要', '标准', '有效', '必须', '要求', '另一种', '其中', '以及'
    }
    
    # 过滤停用词和单字
    filtered = [w for w in words if w not in stop_words and len(w) >= 2]
    
    # 统计并取前N个
    return Counter(filtered).most_common(top_n)

def main():
    # 1. 读取文件
    content = read_notes('notes.txt')
    
    # 2. 提取词语
    words = extract_words(content)
    
    # 3. 统计词频
    top_words = count_top_words(words, top_n=10)
    
    # 4. 输出结果
    print("=" * 30)
    print("考编笔记高频关键词 Top 10")
    print("=" * 30)
    for word, count in top_words:
        print(f"{word}: {count} 次")
    print("=" * 30)

if __name__ == '__main__':
    main()