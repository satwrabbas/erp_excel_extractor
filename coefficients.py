from helpers import get_adjacent_number

def extract_coefficients(rows):
    coeffs = {}
    keywords = ["الطابق", "الشارع", "المصعد", "الوجيبة", "الاتجاه"]
    
    for row in rows:
        for c_idx, cell in enumerate(row):
            if not isinstance(cell, str):
                continue
            text = cell.strip()
            for key in keywords:
                if key in text and key not in coeffs:
                    val = get_adjacent_number(row, c_idx)
                    if val != 0:
                        coeffs[key] = val
    return coeffs