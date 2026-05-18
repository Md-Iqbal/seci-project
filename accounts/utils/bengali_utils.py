"""
Bengali Utility Functions
Helper functions for Bengali number conversion and formatting
"""

def to_bengali_number(number):
    """Convert English numbers to Bengali"""
    bengali_digits = {
        '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
        '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
    }
    
    number_str = str(number)
    bengali_number = ''
    
    for char in number_str:
        bengali_number += bengali_digits.get(char, char)
    
    return bengali_number

def to_english_number(bengali_number):
    """Convert Bengali numbers to English"""
    english_digits = {
        '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
        '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
    }
    
    bengali_str = str(bengali_number)
    english_number = ''
    
    for char in bengali_str:
        english_number += english_digits.get(char, char)
    
    return english_number

def format_bengali_currency(amount):
    """Format currency amount in Bengali"""
    try:
        amount_float = float(amount)
        formatted = f"{amount_float:,.2f}"
        bengali_formatted = to_bengali_number(formatted)
        return f"{bengali_formatted} টাকা"
    except:
        return str(amount)

def get_bengali_month_name(month_number):
    """Get Bengali month name from month number (1-12)"""
    bengali_months = [
        'জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন',
        'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর'
    ]
    
    if 1 <= month_number <= 12:
        return bengali_months[month_number - 1]
    return ''

def format_bengali_date(date_obj):
    """Format date in Bengali"""
    if not date_obj:
        return ''
    
    day = to_bengali_number(date_obj.day)
    month = get_bengali_month_name(date_obj.month)
    year = to_bengali_number(date_obj.year)
    
    return f"{day} {month}, {year}"

def format_bengali_datetime(datetime_obj):
    """Format datetime in Bengali"""
    if not datetime_obj:
        return ''
    
    date_part = format_bengali_date(datetime_obj)
    hour = to_bengali_number(datetime_obj.strftime('%I'))
    minute = to_bengali_number(datetime_obj.strftime('%M'))
    period = 'পূর্বাহ্ন' if datetime_obj.hour < 12 else 'অপরাহ্ন'
    
    return f"{date_part} {hour}:{minute} {period}"

def get_status_bengali(status):
    """Get status label in Bengali"""
    status_map = {
        'PENDING': 'অপেক্ষমাণ',
        'APPROVED': 'অনুমোদিত',
        'REJECTED': 'প্রত্যাখ্যাত'
    }
    return status_map.get(status, status)

def get_account_type_bengali(account_type):
    """Get account type label in Bengali"""
    type_map = {
        'SAVINGS': 'সঞ্চয়ী হিসাব',
        'CURRENT': 'চলতি হিসাব',
        'FD': 'স্থায়ী আমানত'
    }
    return type_map.get(account_type, account_type)

def get_gender_bengali(gender):
    """Get gender label in Bengali"""
    gender_map = {
        'M': 'পুরুষ',
        'F': 'মহিলা',
        'O': 'অন্যান্য'
    }
    return gender_map.get(gender, gender)

# Number to words in Bengali (for amount in words)
def number_to_bengali_words(number):
    """Convert number to Bengali words"""
    # This is a simplified version. For production, use a complete implementation
    ones = ['', 'এক', 'দুই', 'তিন', 'চার', 'পাঁচ', 'ছয়', 'সাত', 'আট', 'নয়']
    tens = ['', '', 'বিশ', 'ত্রিশ', 'চল্লিশ', 'পঞ্চাশ', 'ষাট', 'সত্তর', 'আশি', 'নব্বই']
    teens = ['দশ', 'এগারো', 'বারো', 'তেরো', 'চৌদ্দ', 'পনেরো', 'ষোলো', 'সতেরো', 'আঠারো', 'উনিশ']
    
    try:
        num = int(number)
        if num == 0:
            return 'শূন্য'
        
        # Simplified conversion for numbers up to 99
        if num < 10:
            return ones[num]
        elif num < 20:
            return teens[num - 10]
        elif num < 100:
            return tens[num // 10] + ' ' + ones[num % 10]
        else:
            # For larger numbers, implement full conversion logic
            return to_bengali_number(num)
    except:
        return str(number)