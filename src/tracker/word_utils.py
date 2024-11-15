import win32com.client

def get_word_active_document():
    """Get the active document's file path from Word."""
    try:
        word_app = win32com.client.GetActiveObject("Word.Application")
        active_doc = word_app.ActiveDocument
        if active_doc:
            return active_doc.FullName
    except Exception as e:
        print(f"Error accessing Word document: {e}")
    return None
