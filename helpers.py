import re
import datetime

def get_adjacent_number(row, start_idx):
    """جلب أول رقم بعد الكلمة المفتاحية"""
    for cell in row[start_idx+1:]:
        if isinstance(cell, (int, float)):
            return cell
    return 0

def get_largest_in_first_half(row):
    """يجلب أكبر رقم في أول 8 أعمدة فقط (جدول الدفعات)"""
    first_half = row[:8]
    numbers = [cell for cell in first_half if isinstance(cell, (int, float))]
    return max(numbers) if numbers else 0

def clean_client_name(filename):
    """استخراج اسم العميل من اسم الملف"""
    name = filename.replace('.xlsx', '').replace('.xlsm', '')
    for word in ['متخصص', 'لاحق', 'تخصص', 'مستلم', 'نهائي', 'شقة', 'ملحق', 'ثالث', 'فني', 'رابع']:
        name = name.replace(word, '')
    name = re.sub(r'\d+', '', name)
    return name.strip("- _")

def parse_single_date(cell):
    """تحليل خلية واحدة واستخراج التاريخ منها"""
    if isinstance(cell, datetime.datetime):
        return cell.strftime("%Y-%m-%d")
    if isinstance(cell, str):
        text = cell.strip()
        match = re.search(r'(\d{1,4})[\\/\-](\d{1,2})[\\/\-](\d{1,4})', text)
        if match:
            parts = re.split(r'[\\/\-]', match.group())
            if len(parts[0]) == 4:
                return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
            elif len(parts[2]) == 4:
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return None

def extract_date_from_row(row):
    """يستخرج التاريخ من سطر كامل"""
    for cell in row[:8]:
        date = parse_single_date(cell)
        if date: return date
    return None