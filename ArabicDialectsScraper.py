import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List

# تعريف قائمة الحروف العربية
arabic_letters = ['ا', 'إ', 'أ', 'آ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي', 'پ', 'چ', 'ڥ', 'ڨ', 'گ']

def clean_char_en(text: str) -> str:
    """إزالة الحروف الإنجليزية من النص"""
    return "".join([char for char in text if char.lower() not in 'abcdefghijklmnopqrstuvwxyz'])

def fetch_page(url: str) -> BeautifulSoup:
    """استرجاع وتحليل HTML من عنوان URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # التحقق من نجاح الطلب
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"خطأ في استرجاع الصفحة: {e}")
        return None

def get_details(url: str) -> Dict[str, str]:
    """استخراج تفاصيل من صفحة معينة"""
    soup = fetch_page(url)
    if not soup:
        return {"lahja": "None", "explin": "None"}
    
    dialects = soup.find('div', attrs={"class": "def-main"})
    term = "الجزائرية"
    detail = ""
    
    if dialects:
        term_div = dialects.find("div", attrs={"class": "dialects"})
        body_div = dialects.find("div", attrs={"class": "def-body"})
        
        term = term_div.text.strip() if term_div else term
        detail = body_div.text.strip() if body_div else detail
        
    return {"lahja": ' '.join(term.split()[1:]), "explin": detail}

def scrape_words(harf: str, dialect: str) -> List[Dict[str, str]]:
    """استخراج الكلمات المرتبطة بحرف معين لهجة معينة"""
    dict_all_harfs = []
    url = f"https://ar.mo3jam.com/dialect/{dialect}/words/{harf}#{harf}"
    soup = fetch_page(url)
    
    if not soup:
        print(f"فشل في استرجاع صفحة الكلمات للحرف {harf} للهجة {dialect}")
        return dict_all_harfs
    
    li_hrof = soup.find('ul', attrs={'class': "grid-list"})
    if not li_hrof:
        print(f"لم يتم العثور على قائمة الكلمات للحرف {harf} للهجة {dialect}")
        return dict_all_harfs
    
    for word_element in li_hrof.find_all('a'):
        word = word_element.text.strip()
        term_details = get_details(f"https://ar.mo3jam.com/term/{word}#{dialect}")
        
        one_harf = {
            "harf": harf,
            "words": clean_char_en(word),
            "explin": term_details["explin"],
            "dialect":dialect,
            "link": f"https://ar.mo3jam.com/term/{word}#{dialect}"
        }
        
        dict_all_harfs.append(one_harf)
    
    print(f"تم الانتهاء من جمع بيانات الحرف {harf} للهجة {dialect} ويحتوي على {len(dict_all_harfs)} كلمات")
    return dict_all_harfs

def main(dialects: List[str], file_name: str) -> None:
    """الوظيفة الرئيسية لجمع البيانات وتخزينها"""
    all_harfs_data = []
    
    for dialect in dialects:
        for harf in arabic_letters:
            harf_data = scrape_words(harf, dialect)
            all_harfs_data.extend(harf_data)

        
            
    
    print(f"إجمالي عدد البيانات التي تم جمعها: {len(all_harfs_data)}")
    
    # تحديد المسار الكامل للملف
    file_path = os.path.join(os.getcwd(), file_name)
    
    df = pd.DataFrame(all_harfs_data)
    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"تم حفظ البيانات في {file_path}")

if __name__ == "__main__":
    # تحديد اللهجات واسم الملف
    dialects_list = [ 'Algerian','Egyptian','Moroccan']  # قم بإضافة اللهجات الأخرى هنا
    output_file_name = "words_data.csv"  # تحديد اسم ملف CSV
    
    main(dialects_list, output_file_name)
