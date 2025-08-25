"""
Test script for enhanced clipboard import functionality
"""

import tkinter as tk
from tkinter import ttk
import pyperclip

# Sample Arena deck list for testing
SAMPLE_ARENA_DECK = """Deck
4 Lightning Bolt (M21) 160
4 Counterspell (MH2) 267  
2 Black Lotus (LEA) 232
3 Jace, the Mind Sculptor (WWK) 31
4 Brainstorm (STA) 13
2 Force of Will (EMA) 49
4 Swords to Plowshares (STA) 10
3 Snapcaster Mage (TSR) 86

Sideboard
2 Surgical Extraction (NPH) 74
3 Rest in Peace (A25) 32
2 Flusterstorm (C11) 18
"""

SAMPLE_SIMPLE_DECK = """4x Lightning Bolt
4x Counterspell  
2x Black Lotus
3x Jace, the Mind Sculptor
4x Brainstorm
2x Force of Will
4x Swords to Plowshares
3x Snapcaster Mage

Sideboard:
2x Surgical Extraction
3x Rest in Peace
2x Flusterstorm"""

def test_clipboard_import():
    """Test the clipboard import functionality"""
    
    root = tk.Tk()
    root.title("🧪 Clipboard Import Test")
    root.geometry("600x400")
    
    # Apply theme if available
    try:
        from src.gui.sun_valley_theme import initialize_theme
        theme_manager = initialize_theme(root)
        print("✓ Applied Sun Valley theme for testing")
    except ImportError:
        print("⚠ Sun Valley theme not available")
    
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Header
    header = ttk.Label(main_frame, text="📋 Clipboard Import Testing", 
                      font=('Segoe UI', 16, 'bold'))
    header.pack(pady=(0, 20))
    
    info_label = ttk.Label(main_frame, 
                          text="Test the enhanced clipboard import with progress bars and card images",
                          font=('Segoe UI', 10))
    info_label.pack(pady=(0, 20))
    
    # Sample data buttons
    sample_frame = ttk.LabelFrame(main_frame, text="Load Sample Data to Clipboard", padding=10)
    sample_frame.pack(fill=tk.X, pady=(0, 20))
    
    def load_arena_sample():
        pyperclip.copy(SAMPLE_ARENA_DECK)
        status_var.set("✅ Arena format sample loaded to clipboard")
    
    def load_simple_sample():
        pyperclip.copy(SAMPLE_SIMPLE_DECK)
        status_var.set("✅ Simple format sample loaded to clipboard")
    
    ttk.Button(sample_frame, text="Load Arena Format Sample", 
              command=load_arena_sample).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(sample_frame, text="Load Simple Format Sample", 
              command=load_simple_sample).pack(side=tk.LEFT)
    
    # Test import button
    test_frame = ttk.LabelFrame(main_frame, text="Test Import", padding=10)
    test_frame.pack(fill=tk.X, pady=(0, 20))
    
    def test_import():
        try:
            from src.gui.clipboard_import_dialog import import_clipboard_with_enhanced_dialog
            
            status_var.set("🔄 Starting clipboard import...")
            root.update()
            
            deck = import_clipboard_with_enhanced_dialog(root)
            
            if deck:
                status_var.set(f"✅ Successfully imported deck: '{deck.name}' with {deck.get_total_cards()} cards")
                
                # Show deck summary
                summary_text.delete(1.0, tk.END)
                summary_text.insert(1.0, f"Deck Name: {deck.name}\n")
                summary_text.insert(tk.END, f"Total Cards: {deck.get_total_cards()}\n")
                summary_text.insert(tk.END, f"Created: {deck.created_date}\n\n")
                summary_text.insert(tk.END, "Cards:\n")
                for deck_card in deck.cards:
                    sb_text = " (SB)" if deck_card.sideboard else ""
                    summary_text.insert(tk.END, f"• {deck_card.quantity}x {deck_card.card.name}{sb_text}\n")
            else:
                status_var.set("❌ Import cancelled or failed")
        except Exception as e:
            status_var.set(f"❌ Import error: {str(e)}")
    
    import_btn = ttk.Button(test_frame, text="🎴 Test Enhanced Clipboard Import", 
                           command=test_import, style="Action.TButton")
    import_btn.pack()
    
    # Results area
    results_frame = ttk.LabelFrame(main_frame, text="Import Results", padding=10)
    results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    summary_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
    scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=summary_text.yview)
    summary_text.configure(yscrollcommand=scrollbar.set)
    
    summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Status bar
    status_var = tk.StringVar(value="Ready to test clipboard import")
    status_bar = ttk.Label(main_frame, textvariable=status_var, relief=tk.SUNKEN)
    status_bar.pack(fill=tk.X, pady=(10, 0))
    
    # Initial instructions
    summary_text.insert(1.0, 
        "Instructions:\n"
        "1. Click one of the sample buttons to load test data to clipboard\n"
        "2. Click 'Test Enhanced Clipboard Import' to see the progress dialog\n"
        "3. Watch the progress bar and card images during import\n\n"
        "The import will show each card with enhanced Scryfall data and artwork!"
    )
    
    root.mainloop()

if __name__ == "__main__":
    test_clipboard_import()
