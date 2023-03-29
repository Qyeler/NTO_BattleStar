from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

def create_pdf_with_image_and_sum(image_path, pdf_path, image_size, amount):
    c = Canvas(pdf_path, pagesize=letter)

    # Открываем и читаем изображение
    img = ImageReader(image_path)

    # Определяем размеры изображения
    img_width, img_height = img.getSize()

    # Вычисляем размеры и координаты изображения в pdf файле
    aspect_ratio = img_height / float(img_width)
    img_width = image_size * inch
    img_height = img_width * aspect_ratio
    x = 0.5 * (letter[0] - img_width)
    y = 0.5 * (letter[1] - img_height)

    # Рисуем изображение на холсте
    c.drawImage(image_path, x, y + inch + 0.5 * inch, img_width, img_height)

    # Добавляем заголовок документа
    c.setFont('Helvetica', 20)
    c.drawCentredString(letter[0] / 2.0, letter[1] - inch, "Document for the payment period")

    # Добавляем информацию о сумме
    c.setFont('Helvetica', 18)
    c.drawString(inch, inch * 4.5, f'Total cost for period: {amount}')

    # Добавляем переданную информацию
    c.setFont('Helvetica', 20)
    c.drawCentredString(letter[0] / 2.0 , letter[1] - 2.5 * inch + 0.5 * inch, f'Grapg of usage')

    # Сохраняем pdf файл
    c.showPage()
    c.save()