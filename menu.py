import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib
import os
from database import Database
from datetime import datetime

class MenuDisplay:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.create_menu_view()
        
    def create_menu_view(self):
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        main_box.set_margin_bottom(10)
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
            all_dates.update(item.get("dates_served", []))
        
        # Convert to list and sort
        date_list = sorted(list(all_dates))
        
        # Default to today if it exists in the list, otherwise use the first date
        today = datetime.now().strftime("%Y-%m-%d")
        default_date = today if today in date_list else (date_list[0] if date_list else today)
        
        # Date combobox
        self.date_combo = Gtk.ComboBoxText()
        for date in date_list:
            self.date_combo.append_text(date)
        if date_list:
            # Set active date
            for i, date in enumerate(date_list):
                if date == default_date:
                    self.date_combo.set_active(i)
                    break
            if self.date_combo.get_active() < 0:
                self.date_combo.set_active(0)
        
        self.date_combo.connect("changed", self.on_date_changed)
        date_box.pack_start(self.date_combo, False, False, 0)
        
        # Scrolled window for menu items
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        main_box.pack_start(scrolled, True, True, 0)
        
        # Content box for menu items
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scrolled.add(self.content_box)
        
        # Load initial menu
        self.update_menu_display()
    
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