import win32com.client

def get_excel_active_workbook():
    """Get the active workbook's file path from Excel."""
    try:
        excel_app = win32com.client.GetActiveObject("Excel.Application")
        active_workbook = excel_app.ActiveWorkbook
        if active_workbook:
            return active_workbook.FullName
    except Exception as e:
        print(f"Error accessing Excel workbook: {e}")
    return None
