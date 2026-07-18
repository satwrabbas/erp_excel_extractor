from helpers import get_adjacent_number, clean_client_name, to_float

def extract_basic_info(rows, file_name):
    info = {
        'contract_type': 'متخصص',
        'client_name': 'غير محدد',
        'guarantor': 'بدون كفيل',
        'area': 0.0,
        'base_price': 0.0,
        'down_payment': 0.0,
        'monthly_installment': 0.0,
        'is_finalized': False
    }

    for r_idx, row in enumerate(rows):
        for c_idx, cell in enumerate(row):
            if not isinstance(cell, str):
                continue
            text = cell.strip()

            if "لاحق" in text:
                info['contract_type'] = 'لاحق التخصص'
            if "تصفية" in text or "مستلم نهائي" in text:
                info['is_finalized'] = True
                info['contract_type'] = 'مستلم'

            if text == "المالك" or "اسم الفريق الثاني" in text:
                if r_idx + 1 < len(rows):
                    for val in rows[r_idx + 1][c_idx:]:
                        if isinstance(val, str) and len(val.strip()) > 3:
                            info['client_name'] = val.strip()
                            break

            if text == "الكفيل":
                if r_idx + 1 < len(rows):
                    for val in rows[r_idx + 1][c_idx:]:
                        if isinstance(val, str) and len(val.strip()) > 3:
                            info['guarantor'] = val.strip()
                            break

            if "مساحة الشقة" in text and info['area'] == 0:
                info['area'] = get_adjacent_number(row, c_idx)
            
            if "سعر المتر المربع" in text and info['base_price'] == 0:
                info['base_price'] = get_adjacent_number(row, c_idx)

    if info['client_name'] == 'غير محدد' or info['client_name'] == 'رقم الفريق الثاني':
        info['client_name'] = clean_client_name(file_name)

    return info