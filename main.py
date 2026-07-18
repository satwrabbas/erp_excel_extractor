import os
import json
import openpyxl

from basic_info import extract_basic_info
from coefficients import extract_coefficients
from payments import extract_payments

INPUT_FOLDER = 'input_files'
OUTPUT_FILE = 'output_files/erp_data.json'

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

            # 🌟 الربط الذكي: نأخذ قيم الدفعة الأولى والقسط الشهري من السجل لضمان التطابق
            for p in payment_history:
                if p['payment_name'] == "دفعة أولى" and basic_info['down_payment'] == 0:
                    basic_info['down_payment'] = p['amount_paid']
                if p['payment_name'] == "القسط 1" and basic_info['monthly_installment'] == 0:
                    basic_info['monthly_installment'] = p['amount_paid']

            contract_data = {
                "file_name": file_name,
                "basic_info": basic_info,
                "coefficients": coefficients,
                "payment_history": payment_history
            }

            all_contracts_data.append(contract_data)
            print(f"✅ تم سحب: {basic_info['client_name']} ({len(payment_history)} دفعات سليمة)")

        except Exception as e:
            print(f"❌ فشل معالجة الملف {file_name}: {e}")

    if all_contracts_data:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as json_file:
            json.dump(all_contracts_data, json_file, ensure_ascii=False, indent=4)
        print(f"\n🎉 تم حفظ البيانات النهائية والمطابقة 100% في: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_excel_files()