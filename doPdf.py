from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
import calcsum
def create_pdf_with_image_and_sum(image_path, pdf_path, image_size, amount,amout_wats):
    c = Canvas(pdf_path, pagesize=letter)

    img = ImageReader(image_path)

    img_width, img_height = img.getSize()
    aspect_ratio = img_height / float(img_width)
    img_width = image_size * inch
    img_height = img_width * aspect_ratio
    x = 0.5 * (letter[0] - img_width)
    y = 0.5 * (letter[1] - img_height)

    c.drawImage(image_path, x, y + inch + 0.5 * inch, img_width, img_height)

    c.setFont('Helvetica', 20)
    c.drawCentredString(letter[0] / 2.0, letter[1] - inch, "Document for the payment period")

    c.setFont('Helvetica', 18)
    c.drawString(inch, inch * 4.5, f'Total powur usage for month: {amout_wats}')
    c.drawString(inch, inch * 4.5, f'Total cost for month: {amount}')

    c.setFont('Helvetica', 20)
    c.drawCentredString(letter[0] / 2.0 , letter[1] - 2.5 * inch + 0.5 * inch, f'Grapg of usage')

    c.showPage()
    c.save()