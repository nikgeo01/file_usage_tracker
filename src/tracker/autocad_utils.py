import win32com.client

def get_autocad_active_document():
    """Get the active document's file path from AutoCAD."""
    try:
        acad_app = win32com.client.GetActiveObject("AutoCAD.Application")
        active_doc = acad_app.ActiveDocument
        if active_doc:
            return active_doc.FullName
    except Exception as e:
        print(f"Error accessing AutoCAD document: {e}")
    return None
