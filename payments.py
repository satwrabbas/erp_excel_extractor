from helpers import get_largest_in_first_half, extract_date_from_row, parse_single_date, to_float

def extract_payments(rows):
    payments = []
    
    amount_col = -1
    price_col = -1
    date_col = -1
    
    # 1. البحث عن الأعمدة الصحيحة (في أول 8 أعمدة فقط لتجنب جدول المعاملات الأيسر)
    for row in rows[:20]: 
        for c_idx, cell in enumerate(row[:8]):
            if isinstance(cell, str):
                text = cell.strip()
                # تثبيت العمود فقط في حال لم نجده بعد
                if amount_col == -1 and ("قيمة القسط" in text or "المبلغ" in text):
                    amount_col = c_idx
                elif price_col == -1 and ("سعر المتر" in text):
                    price_col = c_idx
                elif date_col == -1 and ("تاريخ القسط" in text or text == "التاريخ" or text == "تاريخ الدفع"):
                    date_col = c_idx

    # 2. سحب البيانات بدقة جراحية
    for row in rows:
        for c_idx, cell in enumerate(row[:5]):
            if isinstance(cell, str):
                text = cell.strip()
                if text.startswith("القسط") or text == "دفعة أولى" or text.startswith("ايصال"):
                    
                    payment_name = text
                    amount = 0.0
                    meter_price = 0.0
                    date = None

                    # أخذ المبلغ بدقة من العمود
                    if amount_col != -1 and amount_col < len(row):
                        amount = to_float(row[amount_col])
                    else:
                        amount = get_largest_in_first_half(row)
                        
                    # أخذ سعر المتر بدقة من العمود
                    if price_col != -1 and price_col < len(row):
                        meter_price = to_float(row[price_col])
                    else:
                        nums = [to_float(c) for c in row[:8] if c is not None and to_float(c) > 0]
                        if amount in nums: nums.remove(amount)
                        if nums: meter_price = max(nums)

                    # أخذ التاريخ
                    if date_col != -1 and date_col < len(row):
                        date = parse_single_date(row[date_col])
                    if not date:
                        date = extract_date_from_row(row)

                    # 🚫 الفلترة الحاسمة: إذا كان المبلغ صفر، فهذا يعني أن القسط فارغ في الإكسل (وهمي) ولن نضيفه!
                    if amount > 100: 
                        payments.append({
                            "payment_name": payment_name,
                            "amount_paid": amount,
                            "meter_price_at_payment": meter_price, 
                            "payment_date": date if date else "2020-01-01"
                        })
                    break 
                
    return payments