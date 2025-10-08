#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生选座系统
功能：让学生在线选择座位并填写个人信息，生成Excel文件供座位分配程序使用
"""

from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)


# 数据库初始化
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('seat_selection.db')
    cursor = conn.cursor()
    
    # 创建学生信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seat_number TEXT UNIQUE NOT NULL,
            student_name TEXT NOT NULL,
            student_id TEXT NOT NULL,
            created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def get_selected_seats():
    """获取已选座位列表"""
    conn = sqlite3.connect('seat_selection.db')
    cursor = conn.cursor()
    cursor.execute('SELECT seat_number FROM students')
    selected = [row[0] for row in cursor.fetchall()]
    conn.close()
    return selected


def get_all_students():
    """获取所有学生信息"""
    conn = sqlite3.connect('seat_selection.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT seat_number, student_name, student_id, created_time '
        'FROM students ORDER BY seat_number'
    )
    students = cursor.fetchall()
    conn.close()
    return students


@app.route('/')
def index():
    """主页面 - 显示选座界面"""
    selected_seats = get_selected_seats()
    # 座位号01-48
    all_seats = [f"{i:02d}" for i in range(1, 49)]
    return render_template('seat_selection.html',
                           all_seats=all_seats,
                           selected_seats=selected_seats)


@app.route('/api/select_seat', methods=['POST'])
def select_seat():
    """选择座位API"""
    data = request.json
    seat_number = data.get('seat_number')
    student_name = data.get('student_name', '').strip()
    student_id = data.get('student_id', '').strip()
    
    # 验证输入
    if not seat_number or not student_name or not student_id:
        return jsonify({'success': False, 'message': '请填写完整信息'})
    
    if not (1 <= int(seat_number) <= 48):
        return jsonify({'success': False, 'message': '座位号无效'})
    
    # 格式化座位号
    formatted_seat = f"{int(seat_number):02d}"
    
    conn = sqlite3.connect('seat_selection.db')
    cursor = conn.cursor()
    
    try:
        # 检查座位是否已被选择
        cursor.execute(
            'SELECT id FROM students WHERE seat_number = ?',
            (formatted_seat,)
        )
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '该座位已被选择'})
        
        # 检查学生是否已经选过座位
        cursor.execute(
            'SELECT id FROM students WHERE student_id = ?',
            (student_id,)
        )
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '您已经选择过座位了'})
        
        # 插入新记录
        cursor.execute('''
            INSERT INTO students (seat_number, student_name, student_id)
            VALUES (?, ?, ?)
        ''', (formatted_seat, student_name, student_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'成功选择座位{formatted_seat}'})
        
    except sqlite3.Error:
        conn.close()
        return jsonify({'success': False, 'message': '数据库错误'})


@app.route('/api/get_selected_seats')
def get_selected_seats_api():
    """获取已选座位的API"""
    selected_seats = get_selected_seats()
    return jsonify({'selected_seats': selected_seats})


@app.route('/admin')
def admin():
    """管理员界面 - 查看所有选座信息"""
    students = get_all_students()
    return render_template('admin.html', students=students)


@app.route('/api/export_excel')
def export_excel():
    """导出Excel文件"""
    students = get_all_students()
    
    if not students:
        return jsonify({'success': False, 'message': '暂无数据'})
    
    # 创建DataFrame
    df_data = []
    for seat_number, student_name, student_id, created_time in students:
        df_data.append({
            '考号': seat_number,  # 座位号作为考号
            '姓名': student_name,
            '学号': student_id
        })
    
    df = pd.DataFrame(df_data)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'seat_selection_{timestamp}.xlsx'
    filepath = os.path.join(os.getcwd(), filename)
    
    # 保存Excel文件
    df.to_excel(filepath, index=False, engine='openpyxl')
    
    return send_file(filepath, as_attachment=True, download_name=filename)


@app.route('/api/clear_data', methods=['POST'])
def clear_data():
    """清空所有数据"""
    conn = sqlite3.connect('seat_selection.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students')
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '数据已清空'})


if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    print("="*50)
    print("学生选座系统启动中...")
    print("请将以下链接发送给学生：")
    print("http://localhost:5055")
    print("管理员界面：http://localhost:5055/admin")
    print("="*50)
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5055, debug=True)