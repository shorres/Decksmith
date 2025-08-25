"""
Test Enhanced Import Dialog
"""

import tkinter as tk
from tkinter import messagebox
from src.gui.enhanced_import_dialog import EnhancedCSVImporter

def test_import():
    """Test the enhanced import dialog"""
    root = tk.Tk()
    root.title("Import Dialog Test")
    root.geometry("300x150")
    
    def test_csv_import():
        """Test CSV import with dialog"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Select Test Deck File",
                filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                importer = EnhancedCSVImporter(root)
                file_type = "arena" if filename.endswith('.txt') else "csv"
                deck = importer.import_deck_with_progress(filename, file_type)
                
                if deck:
                    messagebox.showinfo("Success", f"Imported deck '{deck.name}' with {len(deck.cards)} cards!")
                else:
                    messagebox.showinfo("Cancelled", "Import was cancelled.")
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    # Create test button
    btn = tk.Button(root, text="Test Enhanced Import", command=test_csv_import, 
                   font=('TkDefaultFont', 12), padx=20, pady=10)
    btn.pack(expand=True)
    
    # Instructions
    label = tk.Label(root, text="Click to test the enhanced import dialog\nwith progress bar and card images", 
                    justify=tk.CENTER)
    label.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_import()
