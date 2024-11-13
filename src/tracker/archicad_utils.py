import win32com.client

def get_archicad_active_document():
    """Get the active document's file path from ArchiCAD."""
    try:
        # Connect to the running instance of ArchiCAD
        print("Attempting to connect to ArchiCAD...")
        archi_app = win32com.client.GetActiveObject("ArchiCAD.Application")
        print("Connection successful.")
        
        # Check for an active document
        active_doc = archi_app.ActiveDocument
        if active_doc:
            print(f"Active document found: {active_doc.FullName}")
            return active_doc.FullName  # Retrieves the full file path of the active document
        else:
            print("No active document found in ArchiCAD.")
    except Exception as e:
        print(f"Error accessing ArchiCAD document: {e}")
    return None
