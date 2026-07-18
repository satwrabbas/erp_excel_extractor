import os
import pandas as pd
import openpyxl

# إعداد مسارات المجلدات
INPUT_FOLDER = 'input_files'
OUTPUT_FILE = 'output_files/clean_contracts_data.csv'

def find_value_by_keyword(sheet, keywords):
    """
    دالة سحرية: تبحث عن الكلمة المفتاحية في كل خلايا الشيت.
    إذا وجدتها، تقوم بإرجاع القيمة الموجودة في الخلية التي بجانبها (في العمود التالي).
    """
    for row in sheet.iter_rows(values_only=True):
        for col_idx, cell_value in enumerate(row):
            if cell_value and isinstance(cell_value, str):
                # التحقق إذا كانت أي من الكلمات المفتاحية موجودة في الخلية
                if any(keyword in cell_value for keyword in keywords):
                    # إرجاع القيمة الموجودة في العمود الذي يليه مباشرة
                    if col_idx + 1 < len(row):
                        return row[col_idx + 1]
    return None

def process_excel_files():
    all_extracted_data = []
    
    # جلب جميع ملفات الإكسل من المجلد
    excel_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.xlsx')]
    
    print(f"🔍 تم العثور على {len(excel_files)} ملفات إكسل. جاري المعالجة...")
    
    for file_name in excel_files:
        file_path = os.path.join(INPUT_FOLDER, file_name)
        
        try:
            # فتح ملف الإكسل (data_only=True لجلب القيم الفعلية بدلاً من المعادلات)
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active # نأخذ الورقة الأولى
            
            # 💡 هنا نضع الكلمات المفتاحية التي نبحث عنها بناءً على ملفاتك!
            client_name = find_value_by_keyword(sheet, ['اسم الفريق الثاني', 'العميل', 'المستلم'])
            contract_date = find_value_by_keyword(sheet, ['تاريخ التوقيع', 'التاريخ'])
            apartment_area = find_value_by_keyword(sheet, ['مساحة الشقة', 'المساحة الاجمالية'])
            meter_price = find_value_by_keyword(sheet, ['سعر المتر المربع عند التوقيع', 'سعر المتر الأساسي'])
            down_payment = find_value_by_keyword(sheet, ['دفعة أولى', 'الدفعة المقدمة'])
            
            # يمكنك إضافة المزيد من الحقول هنا بنفس الطريقة...

            # إضافة البيانات المستخرجة إلى القائمة
            extracted_record = {
                'file_name': file_name,
                'client_name': client_name,
                'contract_date': contract_date,
                'total_area': apartment_area,
                'base_meter_price': meter_price,
                'down_payment': down_payment
            }
            
            all_extracted_data.append(extracted_record)
            print(f"✅ تمت معالجة: {file_name}")
            
        except Exception as e:
            print(f"❌ خطأ في معالجة الملف {file_name}: {e}")
            
    # تحويل القائمة إلى جدول بيانات Pandas وحفظه كملف CSV مسطح ونظيف!
    if all_extracted_data:
        df = pd.DataFrame(all_extracted_data)
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"\n🎉 انتهت المهمة! تم حفظ البيانات النظيفة في: {OUTPUT_FILE}")
    else:
        print("\n⚠️ لم يتم استخراج أي بيانات.")

if __name__ == "__main__":
    process_excel_files()