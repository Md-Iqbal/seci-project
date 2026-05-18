from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from django.conf import settings
import os

class SonaliBankFormPDF:
    def __init__(self, application):
        self.application = application
        self.width, self.height = A4
        
        # Register Bengali font
        font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'Nikosh.ttf')
        if not os.path.exists(font_path):
            font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Nikosh.ttf')
        
        try:
            pdfmetrics.registerFont(TTFont('Nikosh', font_path))
        except:
            # Fallback to system font
            pass
    
    def draw_header(self, c):
        """Draw the header with logo and title"""
        # Blue header background
        c.setFillColor(colors.HexColor('#003366'))
        c.rect(20*mm, self.height - 50*mm, self.width - 40*mm, 35*mm, fill=1, stroke=0)
        
        # Logo (sun symbol)
        c.setFillColor(colors.white)
        c.circle(40*mm, self.height - 32*mm, 8*mm, fill=1)
        
        # Title in Bengali
        c.setFont('Nikosh', 18)
        c.setFillColor(colors.white)
        c.drawCentredString(self.width/2, self.height - 25*mm, 'সোনালী ব্যাংক পিএলসি')
        
        # Subtitle
        c.setFont('Nikosh', 10)
        c.drawCentredString(self.width/2, self.height - 32*mm, '................................................শাখা')
        c.drawCentredString(self.width/2, self.height - 38*mm, 'হিসাব খোলার ফরম')
        c.drawCentredString(self.width/2, self.height - 43*mm, 'ব্যক্তিক হিসাব')
        
        # Account number boxes
        c.setFillColor(colors.white)
        c.setFont('Nikosh', 8)
        c.drawString(self.width - 80*mm, self.height - 25*mm, 'হিসাব নম্বর')
        
        # Draw account number boxes
        x_start = self.width - 80*mm
        y_pos = self.height - 30*mm
        for i in range(13):
            c.rect(x_start + i*5*mm, y_pos, 4*mm, 5*mm, stroke=1, fill=0)
        
        # Bank use only text
        c.setFont('Nikosh', 7)
        c.drawString(self.width - 80*mm, self.height - 40*mm, 'ইউনিক গ্রাহক আইডি নম্বর (ব্যাংক)')
        
        # Draw boxes for unique ID
        for i in range(10):
            c.rect(x_start + i*5*mm, self.height - 45*mm, 4*mm, 5*mm, stroke=1, fill=0)
        
        c.setFillColor(colors.black)
        c.drawString(self.width - 35*mm, self.height - 48*mm, '(ব্যাংকের ব্যবহারের জন্য)')
    
    def draw_salutation(self, c, y_pos):
        """Draw salutation section"""
        c.setFont('Nikosh', 9)
        
        # Date line
        c.drawString(25*mm, y_pos, 'তারিখ:..................................')
        c.drawString(self.width - 80*mm, y_pos, 'শাখার ম্যানেজার')
        
        y_pos -= 5*mm
        c.drawString(25*mm, y_pos, 'জনাব/জনাবা')
        
        y_pos -= 5*mm
        c.drawString(25*mm, y_pos, 'সোনালী ব্যাংক পিএলসি')
        
        y_pos -= 5*mm
        c.drawString(25*mm, y_pos, '................................................ শাখা।')
        
        y_pos -= 8*mm
        c.drawString(25*mm, y_pos, 'প্রিয় মহোদয়,')
        
        y_pos -= 6*mm
        text = 'আমি/আমরা আপনার শাখার একটি হিসাব খোলার জন্য আবেদন করছি। আমার/আমাদের হিসাব সংক্রান্ত ও ব্যক্তিগত তথ্য নিচে প্রদান করা হলো।'
        c.drawString(25*mm, y_pos, text)
        
        y_pos -= 6*mm
        c.setFont('Nikosh', 8)
        c.drawCentredString(self.width/2, y_pos, '[ নমুনা অংশ: হিসাব সংক্রান্ত তথ্যাদি ]')
        
        return y_pos - 5*mm
    
    def draw_section_1(self, c, y_pos):
        """Section 1: Account Information"""
        c.setFont('Nikosh', 9)
        
        # 1. Account title
        c.drawString(25*mm, y_pos, '১। হিসাবের শিরোনাম: (বাংলায়).................................................')
        
        y_pos -= 5*mm
        c.drawString(25*mm, y_pos, 'In English (Block Letter):.................................................')
        
        # 2. Account type with checkboxes
        y_pos -= 8*mm
        c.drawString(25*mm, y_pos, '২। হিসাবের প্রকৃতি (টিক চিহ্ন):')
        
        # First row of checkboxes
        y_pos -= 5*mm
        self._draw_checkbox(c, 60*mm, y_pos, '১খানি')
        self._draw_checkbox(c, 90*mm, y_pos, 'চলতি')
        self._draw_checkbox(c, 120*mm, y_pos, 'এসএনডি')
        self._draw_checkbox(c, 150*mm, y_pos, 'এফসি')
        
        # Second row
        y_pos -= 5*mm
        self._draw_checkbox(c, 60*mm, y_pos, 'আরএফসিডি')
        self._draw_checkbox(c, 90*mm, y_pos, 'এনএফসিডি')
        self._draw_checkbox(c, 120*mm, y_pos, 'অন্যান্য')
        
        # 3. Currency
        y_pos -= 8*mm
        c.drawString(25*mm, y_pos, '৩। মুদ্রা (টিক চিহ্ন):')
        
        y_pos -= 5*mm
        self._draw_checkbox(c, 60*mm, y_pos, 'টাকা')
        self._draw_checkbox(c, 90*mm, y_pos, 'ডলার')
        self._draw_checkbox(c, 120*mm, y_pos, 'ইউরো')
        self._draw_checkbox(c, 150*mm, y_pos, 'পাউন্ড সাক্য')
        
        y_pos -= 5*mm
        self._draw_checkbox(c, 60*mm, y_pos, 'এনকরকাত')
        self._draw_checkbox(c, 90*mm, y_pos, 'ষোয়াআল')
        self._draw_checkbox(c, 120*mm, y_pos, 'ইয়ে কেনো একজন')
        self._draw_checkbox(c, 150*mm, y_pos, 'অন্যান্য')
        
        y_pos -= 5*mm
        c.drawString(60*mm, y_pos, 'যে কেনো একজন অথবা জীবিতকজন')
        c.drawString(150*mm, y_pos, 'অন্যান্য................')
        
        # 4. Operating method
        y_pos -= 8*mm
        c.drawString(25*mm, y_pos, '৪। প্রাথমিক জমার পরিমাণ (সংখ্যা)................................................ (টাকা)................................................')
        
        y_pos -= 6*mm
        c.setFont('Nikosh', 8)
        c.drawCentredString(self.width/2, y_pos, '[ দ্বিতীয় অংশ: ব্যক্তি সংক্রান্ত তথ্যাদি ]')
        
        return y_pos - 5*mm
    
    def draw_section_2(self, c, y_pos):
        """Section 2: Personal Information"""
        c.setFont('Nikosh', 9)
        
        # Photo box on right
        photo_x = self.width - 45*mm
        photo_y = y_pos - 40*mm
        c.rect(photo_x, photo_y, 25*mm, 30*mm, stroke=1)
        c.setFont('Nikosh', 7)
        c.drawCentredString(photo_x + 12.5*mm, photo_y + 15*mm, 'হিসাবধারীর ছবি')
        
        # Personal details
        c.setFont('Nikosh', 9)
        c.drawString(25*mm, y_pos, '১। হিসাবধারীর নাম (বাংলায়):.................................................')
        
        y_pos -= 5*mm
        c.drawString(25*mm, y_pos, 'In English (Block Letter):.................................................')
        
        y_pos -= 6*mm
        c.drawString(25*mm, y_pos, '২। জন্ম তারিখ         :.................................................')
        
        y_pos -= 6*mm
        c.drawString(25*mm, y_pos, '৩। পিতার নাম         :.................................................')
        c.drawString(self.width - 80*mm, y_pos, 'হিসাবধারীর ছবি')
        
        y_pos -= 6*mm
        c.drawString(25*mm, y_pos, '৪। মাতার নাম         :.................................................')
        
        y_pos -= 6*mm
        c.drawString(25*mm, y_pos, '৫। স্বামী/স্ত্রীর নাম    :.................................................')
        
        y_pos -= 6*mm
        c.drawString(25*mm, y_pos, '৬। জাতীয়তা          :................................................ ৭। লিঙ্গ:............................................')
        
        y_pos -= 6*mm
        c.setFont('Nikosh', 8)
        c.drawString(25*mm, y_pos, '(বিদেশীদের বিক্ষোর বাণিজ্য করে বিক্রমাস বাণিজ্যাধ্যাক্ষের গণ্য আবাসভূমিকাস্থীয় তড়ে প্রযুক্ত হইবে প্রদান করতে হবে)')
        
        y_pos -= 6*mm
        c.setFont('Nikosh', 9)
        c.drawString(25*mm, y_pos, '৮। রেসিডেন্ট স্ট্যাটাস (টিক চিহ্ন):')
        self._draw_checkbox(c, 80*mm, y_pos, 'রেসিডেন্ট')
        self._draw_checkbox(c, 110*mm, y_pos, 'নন-রেসিডেন্ট')
        
        y_pos -= 5*mm
        c.setFont('Nikosh', 7)
        text = '(বিদেশীদের সাথে কারবার করতে পরর্তী বিদেশী মুদ্রার বিনিময় লেনদেন সংক্রান্ত ব্যাংক তড়ে প্রযোজন করতে হবে)'
        c.drawString(30*mm, y_pos, text)
        
        return y_pos - 8*mm
    
    def draw_section_2_continued(self, c, y_pos):
        """Continue Section 2"""
        c.setFont('Nikosh', 9)
        
        c.drawString(25*mm, y_pos, '১০। পেশার ঠিক        :.................................................')
        
        y_pos -= 6*mm
        c.drawString(25*mm, y_pos, '১১। অর্থের উৎস (বিদরিত) :.................................................')
        
        y_pos -= 6*mm
        c.drawString(25*mm, y_pos, '১২। ট্যাক্স আইডি নম্বর (TIN) (যদি থাকে) :.................................................')
        
        y_pos -= 8*mm
        c.drawString(25*mm, y_pos, '১৩। (ক) বর্তমান ঠিকানা: সড়ক/গ্রাম:.................................................পোস্ট:.................................................')
        
        y_pos -= 5*mm
        c.drawString(30*mm, y_pos, 'থানা:................................................(জেলা):.................................................')
        
        y_pos -= 5*mm
        c.drawString(30*mm, y_pos, 'ফোন/মোবাইল নম্বর:................................................ই-মেইল:.................................................')
        
        y_pos -= 6*mm
        c.drawString(25*mm, y_pos, '     (খ) স্থায়ী ঠিকানা: সড়ক/গ্রাম:.................................................পোস্ট:.................................................')
        
        y_pos -= 5*mm
        c.drawString(30*mm, y_pos, 'থানা:................................................(জেলা):.................................................')
        
        y_pos -= 5*mm
        c.drawString(30*mm, y_pos, 'ফোন/মোবাইল নম্বর:................................................ই-মেইল:.................................................')
        
        y_pos -= 8*mm
        c.setFont('Nikosh', 8)
        text = '১। হিসাবধারী একরেখি করলেভাবে হবে সকলের এবং হিসাবধারী নাবালক হলে হিসাবধারীর অভিভাবক (বাবা অথবা মা অথবা অন্যান্য ইত্যাদি মাগ্র্কে)'
        c.drawString(25*mm, y_pos, text)
        
        y_pos -= 4*mm
        text = 'সংক্রান্ত তথ্যাদি পৃথকভাবে হবিত অভিষেক দৃষ্টি অভিষেকের সম্পত্তি হবেক্ষক নম্বর করতে হবে।'
        c.drawString(28*mm, y_pos, text)
        
        return y_pos - 5*mm
    
    def _draw_checkbox(self, c, x, y, label):
        """Draw a checkbox with label"""
        # Draw square checkbox
        c.rect(x, y, 3*mm, 3*mm, stroke=1, fill=0)
        # Draw label
        c.drawString(x + 4*mm, y, label)
    
    def create_page_1(self, buffer):
        """Create first page"""
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Draw header
        self.draw_header(c)
        
        # Start content
        y_pos = self.height - 55*mm
        
        # Draw salutation
        y_pos = self.draw_salutation(c, y_pos)
        
        # Draw section 1
        y_pos = self.draw_section_1(c, y_pos)
        
        # Draw section 2
        y_pos = self.draw_section_2(c, y_pos)
        
        # Continue section 2
        y_pos = self.draw_section_2_continued(c, y_pos)
        
        c.showPage()
        return c
    
    def create_page_2(self, c):
        """Create second page"""
        # Continue from page 1
        y_pos = self.height - 30*mm
        
        # Add nominee section, signatures, etc.
        # (This would be similar structure)
        
        c.showPage()
        return c
    
    def generate(self):
        """Generate the complete PDF"""
        from io import BytesIO
        buffer = BytesIO()
        
        c = self.create_page_1(buffer)
        c = self.create_page_2(c)
        
        c.save()
        
        pdf = buffer.getvalue()
        buffer.close()
        return pdf