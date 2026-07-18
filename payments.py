from helpers import get_largest_in_first_half, extract_date_from_row, parse_single_date

def extract_payments(rows):
    payments = []
    
    amount_col = -1
    price_col = -1
    date_col = -1
    
    for row in rows[:20]: 
        for c_idx, cell in enumerate(row):
            if isinstance(cell, str):
                text = cell.strip()
                if "قيمة القسط" in text or "المبلغ" in text:
                    amount_col = c_idx
                elif "سعر المتر" in text:
                    price_col = c_idx
                elif "تاريخ القسط" in text or text == "التاريخ":
                    date_col = c_idx

    for row in rows:
        for c_idx, cell in enumerate(row[:5]):
            if isinstance(cell, str):
                text = cell.strip()
                if text.startswith("القسط") or text == "دفعة أولى" or text.startswith("ايصال"):
                    
                    payment_name = text
                    amount = 0
                    meter_price = 0
                    date = None

                    if amount_col != -1 and amount_col < len(row):
                        val = row[amount_col]
                        if isinstance(val, (int, float)): amount = val
                        
                    if price_col != -1 and price_col < len(row):
                        val = row[price_col]
                        if isinstance(val, (int, float)): meter_price = val

                    if date_col != -1 and date_col < len(row):
                        date = parse_single_date(row[date_col])

                    if amount == 0:
                        amount = get_largest_in_first_half(row)
                    
                    if meter_price == 0:
                        nums = [c for c in row[:8] if isinstance(c, (int, float)) and c > 0]
                        if amount in nums:
                            nums.remove(amount)
                        if nums:
                            meter_price = max(nums)

                    if not date:
                        date = extract_date_from_row(row)

                    if amount > 100: 
                        payments.append({
                            "payment_name": payment_name,
                            "amount_paid": amount,
                            "meter_price_at_payment": meter_price, 
                            "payment_date": date if date else "2020-01-01"
                        })
                    break 
                
    return payments