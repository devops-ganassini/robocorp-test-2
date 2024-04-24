from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=0)

    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        embed_screenshot_to_receipt(
            'output/screenshots/order-'+order['Order number']+'.png',
            'output/receipts/receipt-'+order['Order number']+'.pdf'
        )
    archive_receipts()

def open_robot_order_website():
    # TODO: Implement your function here
    browser.goto('https://robotsparebinindustries.com/#/robot-order')

def close_annoying_modal():
    page = browser.page()
    page.click('text=OK')

def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    csv = Tables()
    orders = csv.read_table_from_csv('orders.csv')
    return orders

def fill_the_form(order):
    page = browser.page()
    page.select_option('#head', order['Head'])
    page.locator('#id-body-'+order['Body']).check()
    page.fill('[type=number]', order['Legs'])
    page.fill('#address', order['Address'])
    page.click('#order')

    while page.locator('.alert-danger').is_visible():
        page.click('#order')

    page.screenshot(path='output/screenshots/order-'+order['Order number']+'.png')
    store_receipt_as_pdf(order['Order number'])

    page.click('#order-another')

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt_html, "output/receipts/receipt-"+order_number+".pdf")

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.open_pdf(pdf_file)
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts', 'output/receipts.zip')
