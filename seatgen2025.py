import pandas as pd
import os
import unicodedata

def process_student_data():
    """
    处理2025mt.xlsx文件，根据学生9位考号结构生成座位表文件
    考号结构：9位数字
    - 倒数3-4位（第6-7位）：班级号
    - 最后两位（第8-9位）：座位号
    """
    try:
        # 读取2025mt.xlsx文件
        df = pd.read_excel('2025mt.xlsx')
        print(f"成功读取文件，共{len(df)}条学生记录")
        
        # 显示文件结构信息
        print("文件列名:", df.columns.tolist())
        print("前几行数据:")
        print(df.head())
        
        # 检查并标准化列名
        df.columns = df.columns.str.strip()
        
        # 假设学生信息的列名可能包含：姓名、考号等
        # 根据实际文件结构调整列名
        possible_name_cols = ['姓名', '学生姓名', 'name', '学员姓名']
        possible_id_cols = ['考号', '学号', '准考证号', 'id', '考试号']
        
        name_col = None
        id_col = None
        
        # 寻找姓名列
        for col in possible_name_cols:
            if col in df.columns:
                name_col = col
                break
        
        # 寻找考号列
        for col in possible_id_cols:
            if col in df.columns:
                id_col = col
                break
        
        if name_col is None or id_col is None:
            print("错误：无法找到姓名或考号列")
            print("可用列名:", df.columns.tolist())
            return False
        
        print(f"找到姓名列: {name_col}")
        print(f"找到考号列: {id_col}")
        
        # 清理数据，移除空值
        df = df.dropna(subset=[name_col, id_col])
        
        # 确保考号是数字类型
        df[id_col] = pd.to_numeric(df[id_col], errors='coerce')
        df = df.dropna(subset=[id_col])
        
        # 读取模板文件
        template_file = 'a.cls'
        if not os.path.exists(template_file):
            print(f"错误：模板文件 {template_file} 不存在")
            return False
        
        with open(template_file, 'r', encoding='UTF-8') as file:
            template_data = file.read()
        
        # 按班级号分组学生（考号结构：9位数，倒数3-4位是班级号，最后两位是座位号）
        students_by_class = {}
        for index, row in df.iterrows():
            if pd.isna(row[id_col]):
                continue
            
            student_id = int(row[id_col])
            # 确保是9位考号
            if len(str(student_id)) != 9:
                print(f"警告：考号 {student_id} 不是9位数，跳过")
                continue
                
            # 提取班级号（倒数3-4位）和座位号（最后两位）
            seat_num = student_id % 100  # 最后两位：座位号
            class_num = (student_id // 100) % 100  # 倒数3-4位：班级号
            
            if class_num not in students_by_class:
                students_by_class[class_num] = {}
            
            students_by_class[class_num][seat_num] = {
                'name': str(row[name_col]).strip(),
                'id': student_id,
                'seat_num': seat_num
            }
        
        print(f"按班级号分组完成，共{len(students_by_class)}个班级")
        for class_num, students in students_by_class.items():
            print(f"  班级 {class_num:02d}: {len(students)} 名学生")
        
        # 为每个班级生成座位表
        generated_files = []
        for class_num, students in students_by_class.items():
            if not students:
                continue
                
            print(f"\n正在处理班级 {class_num:02d}...")
            
            # 从模板复制数据
            class_data = template_data
            
            # 替换学生信息
            replaced_count = 0
            for seat_num, student in students.items():
                # 处理座位号格式：个位数不需要前导零，十位数需要前导零
                if seat_num < 10:
                    seat_str = str(seat_num)  # 个位数：1, 2, 3... 9
                else:
                    seat_str = f'{seat_num:02d}'  # 十位数：10, 11... 99
                
                # 原模板中的格式：<name>192.168.19.X</name> 或 <name>192.168.19.XX</name>
                old_pattern = f'<name>192.168.19.{seat_str}</name>'
                new_pattern = f'<name>{seat_num:02d}{student["name"]}</name>'
                
                if old_pattern in class_data:
                    class_data = class_data.replace(old_pattern, new_pattern)
                    print(f"  替换成功：座位{seat_str} -> {student['name']}")
                    replaced_count += 1
                else:
                    print(f"  警告：未找到座位号 {seat_str} 的模板位置")
            
            # 生成输出文件名
            output_filename = f'class_{class_num:02d}.cls'
            
            # 保存文件
            with open(output_filename, 'w', encoding='UTF-8') as file:
                file.write(class_data)
            
            generated_files.append(output_filename)
            print(f"  生成文件: {output_filename} (替换了{replaced_count}个座位)")
        
        print(f"\n处理完成！共生成 {len(generated_files)} 个座位表文件:")
        for filename in generated_files:
            print(f"  - {filename}")
        
        return True
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_files():
    """检查必要的文件是否存在"""
    required_files = ['2025mt.xlsx', 'a.cls']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("错误：以下必要文件不存在:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== 2025年学生座位表生成程序 ===")
    print("正在检查必要文件...")
    
    if not check_files():
        input("按回车键退出...")
        exit(1)
    
    print("开始处理学生数据...")
    success = process_student_data()
    
    if success:
        print("\n✓ 程序执行成功！")
    else:
        print("\n✗ 程序执行失败，请检查错误信息。")
    
    input("按回车键退出...")