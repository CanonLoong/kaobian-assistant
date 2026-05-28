#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识笔记管理系统
用于备考事业单位计算机岗的知识点记录和管理

功能特点：
- 使用 SQLite 数据库存储笔记
- 支持添加、查看、搜索、删除、导出笔记
- 命令行界面，操作简单直观
"""

import sqlite3
import os
from datetime import datetime

# 数据库文件名
DB_NAME = 'notes.db'

def init_database():
    """
    初始化数据库，创建notes表
    
    如果数据库文件不存在则创建，如果表不存在则创建表
    表结构：
    - id: 自增主键
    - title: 标题
    - content: 内容
    - category: 分类（如数据库/网络/操作系统）
    - created_at: 创建时间
    """
    # 连接数据库（如果不存在则自动创建）
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 创建notes表的SQL语句
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        created_at TEXT NOT NULL
    )
    '''
    
    try:
        cursor.execute(create_table_sql)
        conn.commit()
        print("数据库表初始化成功！")
    except sqlite3.Error as e:
        print(f"创建表时出错: {e}")
    finally:
        # 关闭游标和连接
        cursor.close()
        conn.close()

def add_note():
    """
    添加新笔记功能
    
    提示用户输入标题、内容、分类，然后保存到数据库
    """
    print("\n=== 添加新笔记 ===")
    
    # 获取用户输入
    title = input("请输入笔记标题：").strip()
    if not title:
        print("标题不能为空！")
        return
    
    content = input("请输入笔记内容：").strip()
    if not content:
        print("内容不能为空！")
        return
    
    category = input("请输入分类（如：数据库/网络/操作系统）：").strip()
    if not category:
        category = "未分类"
    
    # 获取当前时间
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 连接数据库并插入数据
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # 使用参数化查询防止SQL注入
        insert_sql = '''
        INSERT INTO notes (title, content, category, created_at)
        VALUES (?, ?, ?, ?)
        '''
        cursor.execute(insert_sql, (title, content, category, created_at))
        conn.commit()
        print("笔记添加成功！")
    except sqlite3.Error as e:
        print(f"添加笔记时出错: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def view_all_notes():
    """
    查看所有笔记功能
    
    列出所有笔记，只显示id和标题，方便用户查看概览
    """
    print("\n=== 所有笔记 ===")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # 查询所有笔记，按创建时间降序排列
        cursor.execute('SELECT id, title, category, created_at FROM notes ORDER BY created_at DESC')
        notes = cursor.fetchall()
        
        if not notes:
            print("暂无笔记！")
            return
        
        # 打印表头
        print(f"{'ID':<4} {'分类':<12} {'标题':<30} {'创建时间'}")
        print("-" * 70)
        
        # 打印每条笔记
        for note in notes:
            note_id, title, category, created_at = note
            # 标题过长时截断显示
            display_title = title[:28] + ".." if len(title) > 30 else title
            print(f"{note_id:<4} {category:<12} {display_title:<30} {created_at}")
            
    except sqlite3.Error as e:
        print(f"查询笔记时出错: {e}")
    finally:
        cursor.close()
        conn.close()

def search_notes():
    """
    搜索笔记功能
    
    根据用户输入的关键词，在标题和内容中进行模糊查找
    """
    print("\n=== 搜索笔记 ===")
    
    keyword = input("请输入搜索关键词：").strip()
    if not keyword:
        print("关键词不能为空！")
        return
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # 使用LIKE进行模糊查询，同时搜索title和content
        search_sql = '''
        SELECT id, title, category, created_at FROM notes 
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY created_at DESC
        '''
        # 使用 % 通配符匹配任意字符
        cursor.execute(search_sql, (f'%{keyword}%', f'%{keyword}%'))
        notes = cursor.fetchall()
        
        if not notes:
            print(f"未找到包含 '{keyword}' 的笔记！")
            return
        
        print(f"找到 {len(notes)} 条匹配的笔记：")
        print(f"{'ID':<4} {'分类':<12} {'标题':<30} {'创建时间'}")
        print("-" * 70)
        
        for note in notes:
            note_id, title, category, created_at = note
            display_title = title[:28] + ".." if len(title) > 30 else title
            print(f"{note_id:<4} {category:<12} {display_title:<30} {created_at}")
            
        # 询问是否查看详细内容
        try:
            note_id = int(input("\n请输入要查看详情的笔记ID（输入0返回）："))
            if note_id > 0:
                cursor.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
                note = cursor.fetchone()
                if note:
                    print("\n=== 笔记详情 ===")
                    print(f"ID: {note[0]}")
                    print(f"标题: {note[1]}")
                    print(f"分类: {note[3]}")
                    print(f"创建时间: {note[4]}")
                    print(f"内容:\n{note[2]}")
                else:
                    print("未找到该笔记！")
        except ValueError:
            print("请输入有效的数字！")
            
    except sqlite3.Error as e:
        print(f"搜索笔记时出错: {e}")
    finally:
        cursor.close()
        conn.close()

def delete_note():
    """
    删除笔记功能
    
    根据用户输入的ID删除指定笔记，删除前要求确认
    """
    print("\n=== 删除笔记 ===")
    
    try:
        note_id = int(input("请输入要删除的笔记ID："))
        if note_id <= 0:
            print("ID必须大于0！")
            return
    except ValueError:
        print("请输入有效的数字ID！")
        return
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # 先查询确认笔记存在
        cursor.execute('SELECT title FROM notes WHERE id = ?', (note_id,))
        note = cursor.fetchone()
        
        if not note:
            print("未找到该ID的笔记！")
            return
        
        title = note[0]
        confirm = input(f"确定要删除笔记 '{title}' 吗？(y/N)：").strip().lower()
        
        if confirm == 'y':
            cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            conn.commit()
            print("笔记删除成功！")
        else:
            print("取消删除操作")
            
    except sqlite3.Error as e:
        print(f"删除笔记时出错: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def export_notes():
    """
    导出笔记功能
    
    将所有笔记导出到notes.txt文件，覆盖旧文件
    """
    print("\n=== 导出笔记 ===")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM notes ORDER BY category, created_at DESC')
        notes = cursor.fetchall()
        
        if not notes:
            print("暂无笔记可导出！")
            return
        
        # 打开文件进行写入（覆盖模式）
        with open('notes.txt', 'w', encoding='utf-8') as f:
            for note in notes:
                note_id, title, content, category, created_at = note
                f.write("=" * 60 + "\n")
                f.write(f"ID: {note_id}\n")
                f.write(f"分类: {category}\n")
                f.write(f"标题: {title}\n")
                f.write(f"创建时间: {created_at}\n")
                f.write("-" * 60 + "\n")
                f.write(f"{content}\n")
                f.write("\n")
        
        print(f"成功导出 {len(notes)} 条笔记到 notes.txt！")
        
    except sqlite3.Error as e:
        print(f"导出笔记时出错: {e}")
    except IOError as e:
        print(f"写入文件时出错: {e}")
    finally:
        cursor.close()
        conn.close()

def show_menu():
    """
    显示主菜单
    """
    print("\n" + "=" * 40)
    print("      知识笔记管理系统")
    print("        备考事业单位计算机岗")
    print("=" * 40)
    print("1. 添加笔记")
    print("2. 查看所有笔记")
    print("3. 搜索笔记")
    print("4. 删除笔记")
    print("5. 导出笔记到txt")
    print("0. 退出")
    print("-" * 40)

def main():
    """
    主函数，程序入口
    """
    # 初始化数据库
    init_database()
    
    while True:
        # 显示菜单
        show_menu()
        
        # 获取用户选择
        try:
            choice = int(input("请输入操作编号："))
        except ValueError:
            print("请输入有效的数字！")
            continue
        
        # 根据选择执行对应功能
        if choice == 1:
            add_note()
        elif choice == 2:
            view_all_notes()
        elif choice == 3:
            search_notes()
        elif choice == 4:
            delete_note()
        elif choice == 5:
            export_notes()
        elif choice == 0:
            print("\n感谢使用知识笔记管理系统！")
            print("祝您备考顺利！")
            break
        else:
            print("无效的选择，请输入0-5之间的数字！")
        
        # 操作完成后暂停，等待用户按回车继续
        input("\n按回车键继续...")

if __name__ == '__main__':
    main()
