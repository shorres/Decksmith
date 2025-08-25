#!/usr/bin/env python3
"""
Test script to check emoji rendering in tkinter
"""

import tkinter as tk
from tkinter import ttk


def test_emoji_rendering():
    """Test how various emojis render in tkinter"""
    root = tk.Tk()
    root.title("Emoji Rendering Test")
    root.geometry("600x400")
    
    # Create a text widget to display emojis
    frame = ttk.Frame(root)
    frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    text_widget = tk.Text(frame, wrap=tk.WORD, font=('Segoe UI', 10))
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    text_widget.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')
    
    # Test various emojis used in the app
    emoji_tests = [
        ("Magic Color Symbols (OLD - problematic):", ""),
        ("⚪ White", "White mana symbol"),
        ("🔵 Blue", "Blue mana symbol"), 
        ("⚫ Black", "Black mana symbol"),
        ("🔴 Red", "Red mana symbol"),
        ("🟢 Green", "Green mana symbol"),
        ("", ""),
        ("Magic Color Symbols (NEW - should work):", ""),
        ("[W] White", "White mana symbol"),
        ("[U] Blue", "Blue mana symbol"),
        ("[B] Black", "Black mana symbol"), 
        ("[R] Red", "Red mana symbol"),
        ("[G] Green", "Green mana symbol"),
        ("", ""),
        ("Craft Icons (should render well):", ""),
        ("🔨 Common craft", "Hammer icon"),
        ("🔧 Uncommon craft", "Wrench icon"),
        ("💎 Rare craft", "Diamond icon"),
        ("👑 Mythic craft", "Crown icon"),
        ("", ""),
        ("Status Icons:", ""),
        ("✅ Success/Legal", "Check mark"),
        ("❌ Error/Illegal", "X mark"),
        ("⚠️ Warning/Restricted", "Warning triangle"),
        ("", ""),
        ("UI Icons:", ""),
        ("🎯 Target/Analysis", "Bullseye"),
        ("🔍 Search/Analyze", "Magnifying glass"),
        ("🤖 AI/Robot", "Robot face"),
        ("📊 Statistics", "Bar chart"),
        ("🏗️ Construction", "Building construction"),
        ("⚡ Lightning/Quick", "Lightning bolt"),
        ("🎴 Card", "Playing card"),
        ("🎲 Dice/Random", "Die"),
        ("🔄 Refresh/Cycle", "Arrows forming circle"),
    ]
    
    text_widget.insert('1.0', "EMOJI RENDERING TEST FOR MAGIC TOOL\n")
    text_widget.insert('end', "=" * 50 + "\n\n")
    text_widget.insert('end', "Check how these emojis appear in your system:\n\n")
    
    for emoji_text, description in emoji_tests:
        if emoji_text:
            text_widget.insert('end', f"{emoji_text:<30} ({description})\n")
        else:
            text_widget.insert('end', "\n")
    
    text_widget.insert('end', "\n" + "=" * 50 + "\n")
    text_widget.insert('end', "If any emojis show as boxes, question marks, or black/white shapes,\n")
    text_widget.insert('end', "they should be replaced with text alternatives.\n")
    
    # Make text read-only
    text_widget.config(state='disabled')
    
    root.mainloop()


if __name__ == "__main__":
    print("🧪 Starting emoji rendering test...")
    print("This will open a window showing various emojis used in the Magic Tool.")
    print("Check which ones render properly on your system.")
    test_emoji_rendering()
