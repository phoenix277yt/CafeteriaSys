import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

from database import MenuDatabase

class MenuSystem:
    """Class to handle menu operations and management"""
    
    def __init__(self):
        """Initialize the menu system"""
        self.menu_db = MenuDatabase()
    
    def get_all_menu_items(self):
        """Get all menu items from the database"""
        return self.menu_db.get_all_menu_items()
    
    def get_menu_by_category(self, category):
        """Get menu items filtered by category"""
        return self.menu_db.get_menu_by_category(category)
    
    def add_menu_item(self, name, description, price, category, image=None):
        """Add a new menu item"""
        return self.menu_db.add_menu_item(name, description, price, category, image)
    
    def update_menu_item(self, item_id, **kwargs):
        """Update an existing menu item"""
        return self.menu_db.update_menu_item(item_id, **kwargs)
    
    def delete_menu_item(self, item_id):
        """Delete a menu item"""
        return self.menu_db.delete_menu_item(item_id)

class MenuDisplay:
    def __init__(self, parent):
        self.parent = parent
        self.db = MenuDatabase()
        self.current_date = None
        self.content_box = None
        self.create_menu_view()
    
    def create_menu_view(self):
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        main_box.set_margin_bottom(10)
        
        # Instead of calling pack_start on the parent, add it to the menu_tab
        if hasattr(self.parent, 'menu_tab'):
            self.parent.menu_tab.pack_start(main_box, True, True, 0)
        else:
            # This is likely the menu_tab itself, so we can add directly
            self.parent.pack_start(main_box, True, True, 0)
        
        # Title
        title = Gtk.Label(label="Today's Menu")
        title.get_style_context().add_class("sub-header")
        title.set_margin_bottom(10)
        main_box.pack_start(title, False, False, 0)
        
        # Date selector
        date_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        main_box.pack_start(date_box, False, False, 0)
        
        date_label = Gtk.Label(label="Select Date:")
        date_box.pack_start(date_label, False, False, 5)
        
        # Get all unique dates from menu items
        all_dates = set()
        menu_items = self.db.get_all_menu_items()
        for item in menu_items:
            for date in item.get("dates", []):
                all_dates.add(date)
        
        # Create the date dropdown
        self.date_combo = Gtk.ComboBoxText()
        for date in sorted(all_dates):
            self.date_combo.append_text(date)
        
        # Select first date by default
        if all_dates:
            self.date_combo.set_active(0)
            self.current_date = sorted(all_dates)[0]
        
        self.date_combo.connect("changed", self.on_date_changed)
        date_box.pack_start(self.date_combo, True, True, 0)
        
        # Scrolled window for menu items
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(300)
        main_box.pack_start(scrolled, True, True, 10)
        
        # Content box for menu items
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scrolled.add(self.content_box)
        
        # Update the menu display with current date
        self.update_menu_display()
    
    def create_menu_ui(self, parent):
        # This method is called from main.py, but we already set up the UI in __init__
        # So we don't need to do anything here now
        pass

    def on_date_changed(self, combo):
        self.update_menu_display()
    
    def update_menu_display(self):
        # Clear previous menu items
        for child in self.content_box.get_children():
            self.content_box.remove(child)
        
        # Get selected date
        active = self.date_combo.get_active()
        if active < 0:
            return
        
        selected_date = self.date_combo.get_active_text()
        
        # Get menu items for the selected date
        menu_items = self.db.get_all_menu_items()
        items_for_date = [item for item in menu_items if selected_date in item.get("dates_served", [])]
        
        if not items_for_date:
            label = Gtk.Label(label="No menu items available for this date.")
            label.set_margin_top(20)
            self.content_box.pack_start(label, False, False, 0)
            self.content_box.show_all()
            return
        
        # Display menu items
        for idx, item in enumerate(items_for_date):
            self.create_menu_item_card(item, idx)
        
        self.content_box.show_all()
    
    def create_menu_item_card(self, item, idx):
        # Create a card frame
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        card.get_style_context().add_class("card")
        self.content_box.pack_start(card, False, False, 5)
        
        # Image
        img_path = os.path.join("images", item.get("image", "default.jpg"))
        if os.path.exists(img_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(img_path, 100, 100)
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                card.pack_start(image, False, False, 0)
            except GLib.Error as e:
                print(f"Error loading image {img_path}: {e}")
                image = Gtk.Label(label="No Image")
                card.pack_start(image, False, False, 0)
        else:
            image = Gtk.Label(label="No Image")
            card.pack_start(image, False, False, 0)
        
        # Item details in a vertical box
        details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        card.pack_start(details_box, True, True, 5)
        
        # Item name
        name_label = Gtk.Label()
        name_label.set_markup(f"<b>{item.get('name', 'Unnamed Item')}</b>")
        name_label.set_halign(Gtk.Align.START)
        details_box.pack_start(name_label, False, False, 0)
        
        # Components
        components = item.get("components", [])
        if components:
            comp_text = "Components: " + ", ".join([comp.get("name", "") for comp in components])
            comp_label = Gtk.Label(label=comp_text)
            comp_label.set_halign(Gtk.Align.START)
            details_box.pack_start(comp_label, False, False, 0)