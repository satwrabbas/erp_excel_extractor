import os
import json
import re
import datetime
import openpyxl

INPUT_FOLDER = 'input_files'
OUTPUT_FILE = 'output_files/erp_data.json'

# ==========================================
# 🛠️ دوال المساعدة الذكية
# ==========================================
def get_adjacent_number(row, start_idx):
    """جلب أول رقم بعد الكلمة المفتاحية"""
    for cell in row[start_idx+1:]:
        if isinstance(cell, (int, float)):
            return cell
    return 0

def get_largest_in_first_half(row):
    """🔥 الحل السحري: يجلب أكبر رقم في أول 8 أعمدة فقط (جدول الدفعات) ويتجاهل المعاملات على اليسار"""
    first_half = row[:8]
    numbers = [cell for cell in first_half if isinstance(cell, (int, float))]
    return max(numbers) if numbers else 0

def clean_client_name(filename):
    """🔥 استخراج اسم العميل من اسم الملف في حال فشل البحث الداخلي"""
    name = filename.replace('.xlsx', '').replace('.xlsm', '')
    # إزالة الكلمات الإدارية الملحقة بالاسم
    for word in ['متخصص', 'لاحق', 'تخصص', 'مستلم', 'نهائي', 'شقة', 'ملحق', 'ثالث', 'فني', 'رابع']:
        name = name.replace(word, '')
    # إزالة أي أرقام من الاسم
    name = re.sub(r'\d+', '', name)
    return name.strip("- _")

def extract_date_from_row(row):
    """اصطياد التواريخ بأي صيغة غريبة وتحويلها للصيغة القياسية YYYY-MM-DD"""
    for cell in row:
        if isinstance(cell, datetime.datetime):
            return cell.strftime("%Y-%m-%d")
        
        if isinstance(cell, str):
            text = cell.strip()
            # اصطياد صيغ مثل 2024\8\5 أو 5-10-2023 أو 2023/12/03
            match = re.search(r'(\d{1,4})[\\/\-](\d{1,2})[\\/\-](\d{1,4})', text)
            if match:
                parts = re.split(r'[\\/\-]', match.group())
                if len(parts[0]) == 4: # إذا بدأت بالسنة
                    return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                elif len(parts[2]) == 4: # إذا انتهت بالسنة
                    return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return None

# ==========================================
# 👤 استخراج البيانات الأساسية
# ==========================================
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

            # الأسماء من الداخل
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

            # المساحة والسعر (نأخذ الرقم المجاور)
            if "مساحة الشقة" in text and info['area'] == 0:
                info['area'] = get_adjacent_number(row, c_idx)
            
            if "سعر المتر المربع" in text and info['base_price'] == 0:
                info['base_price'] = get_adjacent_number(row, c_idx)

            # الدفعات (نبحث عن أكبر رقم في النصف الأيمن من الشاشة فقط)
            if text in ["دفعة أولى", "الدفعة المقدمة"] and info['down_payment'] == 0:
                info['down_payment'] = get_largest_in_first_half(row)
                
            if text == "القسط 1" and info['monthly_installment'] == 0:
                info['monthly_installment'] = get_largest_in_first_half(row)

    # 🌟 التعويض الذكي: إذا لم نجد اسم العميل، نستخرجه من اسم الملف
    if info['client_name'] == 'غير محدد' or info['client_name'] == 'رقم الفريق الثاني':
        info['client_name'] = clean_client_name(file_name)

    return info

# ==========================================
# 🧮 استخراج معاملات التميز
# ==========================================
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

# ==========================================
# 💰 استخراج سجل المدفوعات
# ==========================================
def extract_payments(rows):
    payments = []
    
    for row in rows:
        for c_idx, cell in enumerate(row):
            if isinstance(cell, str):
                text = cell.strip()
                # صيد سطر القسط
                if text.startswith("القسط") or text == "دفعة أولى" or text.startswith("ايصال"):
                    
                    # نأخذ أكبر مبلغ في النصف الأيمن فقط لتفادي أرقام المعاملات
                    amount = get_largest_in_first_half(row)
                    date = extract_date_from_row(row)
                    
                    if amount > 100: # تجاهل المبالغ الوهمية (أصغر من 100 ليرة)
                        payments.append({
                            "payment_name": text,
                            "amount_paid": amount,
                            "payment_date": date if date else "2020-01-01"
                        })
                    break # وجدنا بيانات هذا السطر، ننتقل للسطر التالي
                
    return payments

# ==========================================
# 🚀 المنسق الرئيسي
# ==========================================
def process_excel_files():
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
    if not os.path.exists(os.path.dirname(OUTPUT_FILE)):
        os.makedirs(os.path.dirname(OUTPUT_FILE))

    excel_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(('.xlsx', '.xlsm')) and not f.startswith('~$')]
    print(f"🔍 تم العثور على {len(excel_files)} ملفات. جاري التحليل المتقدم...\n")
    
    all_contracts_data = []

    for file_name in excel_files:
        file_path = os.path.join(INPUT_FOLDER, file_name)
        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))

            basic_info = extract_basic_info(rows, file_name)
            coefficients = extract_coefficients(rows)
            payment_history = extract_payments(rows)

            contract_data = {
                "file_name": file_name,
                "basic_info": basic_info,
                "coefficients": coefficients,
                "payment_history": payment_history
            }

            all_contracts_data.append(contract_data)
            print(f"✅ استخراج ناجح: {file_name} -> العميل: {basic_info['client_name']} ({len(payment_history)} حركات مالية)")

        except Exception as e:
            print(f"❌ فشل معالجة الملف {file_name}: {e}")

    if all_contracts_data:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as json_file:
            json.dump(all_contracts_data, json_file, ensure_ascii=False, indent=4)
        print(f"\n🎉 تمت العملية! تم حفظ البيانات النظيفة والمثالية في: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_excel_files()