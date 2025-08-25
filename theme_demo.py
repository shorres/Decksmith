"""
Sun Valley Theme Demo for Magic Tool
"""

import tkinter as tk
from tkinter import ttk
from src.gui.sun_valley_theme import initialize_theme

def create_demo_window():
    """Create a demo window to showcase the Sun Valley theme"""
    root = tk.Tk()
    root.title("Sun Valley Theme Demo - Magic Tool")
    root.geometry("800x600")
    
    # Initialize the theme
    theme_manager = initialize_theme(root)
    
    # Create demo content
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Header
    header_label = ttk.Label(main_frame, text="🎴 Magic: The Gathering Arena Deck Manager", 
                           font=('Segoe UI', 18, 'bold'))
    header_label.pack(pady=(0, 20))
    
    # Theme toggle button
    def toggle_theme():
        new_theme = theme_manager.toggle_theme()
        theme_name = "Dark" if new_theme == "dark" else "Light"
        status_var.set(f"Current theme: {theme_name}")
        toggle_btn.configure(text=f"Switch to {'Light' if new_theme == 'dark' else 'Dark'} Theme")
    
    toggle_btn = ttk.Button(main_frame, text="Switch to Light Theme", 
                          command=toggle_theme, style="Action.TButton")
    toggle_btn.pack(pady=(0, 20))
    
    # Notebook with tabs
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    # Collection tab demo
    collection_frame = ttk.Frame(notebook)
    notebook.add(collection_frame, text="Collection")
    
    collection_label = ttk.Label(collection_frame, text="📚 Your Magic Collection", 
                               font=('Segoe UI', 14, 'bold'))
    collection_label.pack(pady=20)
    
    # Sample treeview
    columns = ('Card', 'Rarity', 'Quantity', 'Set')
    tree = ttk.Treeview(collection_frame, columns=columns, show='headings', height=10)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    
    # Sample data with theme-appropriate tags
    sample_cards = [
        ("Lightning Bolt", "Common", "4", "M21"),
        ("Brainstorm", "Common", "4", "STA"),
        ("Black Lotus", "Rare", "1", "LEA"),
        ("Jace, the Mind Sculptor", "Mythic", "2", "WWK"),
        ("Counterspell", "Uncommon", "4", "MH2")
    ]
    
    for i, (card, rarity, qty, set_code) in enumerate(sample_cards):
        tree.insert('', 'end', values=(card, rarity, qty, set_code), 
                   tags=(rarity.lower(),))
    
    # Apply theme tags
    theme_manager.apply_treeview_tags(tree)
    
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Decks tab demo
    deck_frame = ttk.Frame(notebook)
    notebook.add(deck_frame, text="Decks")
    
    deck_label = ttk.Label(deck_frame, text="⚔️ Your Deck Collection", 
                         font=('Segoe UI', 14, 'bold'))
    deck_label.pack(pady=20)
    
    # Sample buttons
    button_frame = ttk.Frame(deck_frame)
    button_frame.pack(pady=20)
    
    ttk.Button(button_frame, text="New Deck").pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Import from Arena").pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Export to CSV").pack(side=tk.LEFT, padx=5)
    
    # AI Recommendations tab demo
    ai_frame = ttk.Frame(notebook)
    notebook.add(ai_frame, text="AI Recommendations")
    
    ai_label = ttk.Label(ai_frame, text="🤖 AI-Powered Card Suggestions", 
                       font=('Segoe UI', 14, 'bold'))
    ai_label.pack(pady=20)
    
    # Progress bar demo
    progress_frame = ttk.LabelFrame(ai_frame, text="Analysis Progress", padding=10)
    progress_frame.pack(fill=tk.X, padx=20, pady=10)
    
    progress = ttk.Progressbar(progress_frame, mode='determinate', value=75)
    progress.pack(fill=tk.X, pady=10)
    
    progress_label = ttk.Label(progress_frame, text="Analyzing deck synergies... 75%")
    progress_label.pack()
    
    # Status bar
    status_frame = ttk.Frame(root)
    status_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    status_var = tk.StringVar(value="Current theme: Dark")
    status_bar = ttk.Label(status_frame, textvariable=status_var, relief=tk.SUNKEN)
    status_bar.pack(fill=tk.X, padx=5, pady=2)
    
    return root

if __name__ == "__main__":
    demo_root = create_demo_window()
    demo_root.mainloop()
