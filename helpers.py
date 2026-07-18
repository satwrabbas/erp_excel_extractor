import re
import datetime

def to_float(val):
    """تحويل آمن لأي قيمة إلى رقم عشري لتجنب انهيار الكود أو قراءة نصوص"""
    if val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    if isinstance(val, str):
        clean_str = val.replace(',', '').replace(' ', '').strip()
        try:
            return float(clean_str)
        except ValueError:
            return 0.0
    return 0.0

def get_adjacent_number(row, start_idx):
    for cell in row[start_idx+1:]:
        val = to_float(cell)
        if val > 0:
            return val
    return 0.0

def get_largest_in_first_half(row):
    first_half = row[:8]
    numbers = [to_float(cell) for cell in first_half if cell is not None and to_float(cell) > 0]
    return max(numbers) if numbers else 0.0

def clean_client_name(filename):
    name = filename.replace('.xlsx', '').replace('.xlsm', '')
    for word in ['متخصص', 'لاحق', 'تخصص', 'مستلم', 'نهائي', 'شقة', 'ملحق', 'ثالث', 'فني', 'رابع']:
        name = name.replace(word, '')
    name = re.sub(r'\d+', '', name)
    return name.strip("- _")

def parse_single_date(cell):
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
    for cell in row[:8]:
        date = parse_single_date(cell)
        if date: return date
    return None