import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib
import os
from database import Database

class FeedbackSystem:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.selected_item_id = None
        self.component_ratings = {}
        self.create_feedback_ui()
    
    def create_feedback_ui(self):
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        main_box.set_margin_bottom(10)
        self.parent.pack_start(main_box, True, True, 0)
        
        # Title
        title = Gtk.Label(label="Provide Feedback")
        title.get_style_context().add_class("sub-header")
        main_box.pack_start(title, False, False, 10)
        
        # Item selection container
        select_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(select_box, False, False, 0)
        
        # Dish selection label
        select_label = Gtk.Label(label="Select Dish:")
        select_box.pack_start(select_label, False, False, 0)
        
        # Get menu items
        self.menu_items = self.db.get_all_menu_items()
        
        # Dish dropdown
        self.item_combo = Gtk.ComboBoxText()
        for item in self.menu_items:
            self.item_combo.append_text(item["name"])
        self.item_combo.connect("changed", self.on_item_selected)
        select_box.pack_start(self.item_combo, True, True, 0)
        
        # Components frame
        self.components_frame = Gtk.Frame(label="Rate Components")
        self.components_frame.set_margin_top(10)
        main_box.pack_start(self.components_frame, True, True, 0)
        
        # Frame content
        self.components_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.components_box.set_margin_top(10)
        self.components_box.set_margin_start(10)
        self.components_box.set_margin_end(10)
        self.components_box.set_margin_bottom(10)
        self.components_frame.add(self.components_box)
        
        # Submit button container
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        button_box.set_halign(Gtk.Align.END)
        main_box.pack_start(button_box, False, False, 10)
        
        # Submit button
        self.submit_button = Gtk.Button(label="Submit Feedback")
        self.submit_button.set_sensitive(False)  # Disabled initially
        self.submit_button.connect("clicked", self.on_submit_clicked)
        button_box.pack_start(self.submit_button, False, False, 0)
        
        # Load rating images
        self.load_rating_images()
    
    def load_rating_images(self):
        """Load smiley face images for the rating system"""
        self.rating_images = []
        
        # Define paths to rating images
        image_files = [
            "very_sad.png",
            "sad.png",
            "neutral.png",
            "happy.png",
            "very_happy.png"
        ]
        
        # Create default smiley images if they don't exist
        self.create_default_smileys()
        
        # Load images
        for img_file in image_files:
            try:
                img_path = os.path.join("images", img_file)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(img_path, 30, 30)
                self.rating_images.append(pixbuf)
            except GLib.Error as e:
                print(f"Error loading image {img_file}: {e}")
                # Create a fallback colored pixbuf
                self.rating_images.append(None)
    
    def create_default_smileys(self):
        """Create default smiley images if they don't exist"""
        # Check if images directory exists
        if not os.path.exists("images"):
            os.makedirs("images")
            
        # List of default smiley files to create
        smiley_files = [
            ("very_sad.png", "red"),
            ("sad.png", "orange"),
            ("neutral.png", "yellow"),
            ("happy.png", "light green"),
            ("very_happy.png", "green")
        ]
        
        # Create simple colored squares as default images if they don't exist
        for filename, color in smiley_files:
            img_path = os.path.join("images", filename)
            if not os.path.exists(img_path):
                try:
                    # Using PIL to create simple colored images
                    # This requires PIL which we're assuming is installed since we used it before
                    from PIL import Image
                    img = Image.new('RGB', (100, 100), color)
                    img.save(img_path)
                except Exception as e:
                    print(f"Error creating default image {filename}: {e}")
    
    def on_item_selected(self, combo):
        # Clear previous components
        for child in self.components_box.get_children():
            self.components_box.remove(child)
            
        # Clear previous ratings
        self.component_ratings = {}
            
        # Get selected item details
        active = combo.get_active()
        if active < 0:
            return
            
        selected_item_name = combo.get_active_text()
        selected_item = None
        
        for item in self.menu_items:
            if item["name"] == selected_item_name:
                selected_item = item
                self.selected_item_id = item["id"]
                break
                
        if not selected_item:
            return
            
        # Get components
        components = selected_item.get("components", [])
        
        if not components:
            label = Gtk.Label(label="No components found for this item")
            self.components_box.pack_start(label, False, False, 0)
            self.submit_button.set_sensitive(False)
            self.components_box.show_all()
            return
            
        # Enable submit button
        self.submit_button.set_sensitive(True)
        
        # Display components for rating
        for component in components:
            comp_id = component["id"]
            comp_name = component["name"]
            
            # Component container
            comp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.components_box.pack_start(comp_box, False, False, 5)
            
            # Component name
            name_label = Gtk.Label(label=f"{comp_name}:")
            name_label.set_size_request(100, -1)
            name_label.set_halign(Gtk.Align.START)
            comp_box.pack_start(name_label, False, False, 0)
            
            # Rating buttons container
            rating_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            comp_box.pack_start(rating_box, False, False, 0)
            
            # Store the selected rating
            self.component_ratings[comp_id] = 0
            
            # Create rating buttons (smileys)
            rating_buttons = []
            for rating in range(1, 6):
                button = Gtk.Button()
                if self.rating_images[rating-1]:
                    image = Gtk.Image.new_from_pixbuf(self.rating_images[rating-1])
                    button.set_image(image)
                else:
                    button.set_label(str(rating))
                
                # Connect button click
                button.connect("clicked", self.on_rating_clicked, comp_id, rating)
                rating_box.pack_start(button, False, False, 0)
                rating_buttons.append(button)
            
            # Rating label
            self.component_ratings[f"{comp_id}_label"] = Gtk.Label(label="Not rated")
            self.component_ratings[f"{comp_id}_label"].set_size_request(100, -1)
            comp_box.pack_start(self.component_ratings[f"{comp_id}_label"], False, False, 0)
        
        self.components_box.show_all()
    
    def on_rating_clicked(self, button, comp_id, rating):
        """Handle rating button click"""
        self.component_ratings[comp_id] = rating
        
        # Update label
        rating_labels = ["Very Poor", "Poor", "Average", "Good", "Excellent"]
        self.component_ratings[f"{comp_id}_label"].set_label(rating_labels[rating-1])
    
    def on_submit_clicked(self, button):
        """Handle submit button click"""
        # Check if all components are rated
        unrated = []
        for comp_id, rating in self.component_ratings.items():
            if isinstance(comp_id, int) and rating == 0:
                # Get component name
                for item in self.menu_items:
                    if item["id"] == self.selected_item_id:
                        for comp in item["components"]:
                            if comp["id"] == comp_id:
                                unrated.append(comp["name"])
                                break
        
        if unrated:
            dialog = Gtk.MessageDialog(
                transient_for=self.parent.get_toplevel(),
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="Incomplete Feedback",
            )
            dialog.format_secondary_text(f"Please rate the following components: {', '.join(unrated)}")
            dialog.run()
            dialog.destroy()
            return
        
        # Prepare feedback data
        feedback_data = {
            "item_id": self.selected_item_id,
            "item_name": self.item_combo.get_active_text(),
            "ratings": {}
        }
        
        # Add component ratings
        for comp_id, rating in self.component_ratings.items():
            if isinstance(comp_id, int):
                feedback_data["ratings"][comp_id] = rating
                
        # Save feedback
        success = self.db.add_feedback(feedback_data)
        
        if success:
            dialog = Gtk.MessageDialog(
                transient_for=self.parent.get_toplevel(),
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Thank You!",
            )
            dialog.format_secondary_text("Thank you for your feedback!")
            dialog.run()
            dialog.destroy()
            
            # Reset form
            self.item_combo.set_active(-1)
            for child in self.components_box.get_children():
                self.components_box.remove(child)
            self.component_ratings = {}
            self.submit_button.set_sensitive(False)
        else:
            dialog = Gtk.MessageDialog(
                transient_for=self.parent.get_toplevel(),
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error",
            )
            dialog.format_secondary_text("There was an error saving your feedback. Please try again.")
            dialog.run()
            dialog.destroy()
    
    def display_summary(self, parent_window):
        """Display feedback summary in the given window"""
        # Create box for content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_bottom(10)
        parent_window.add(box)
        
        # Title
        title = Gtk.Label(label="Feedback Summary")
        title.get_style_context().add_class("sub-header")
        box.pack_start(title, False, False, 5)
        
        # Get all feedback data
        feedback_data = self.db.get_all_feedback()
        
        if not feedback_data:
            label = Gtk.Label(label="No feedback data available.")
            label.set_margin_top(20)
            box.pack_start(label, False, False, 0)
            parent_window.show_all()
            return
        
        # Create notebook for item tabs
        notebook = Gtk.Notebook()
        box.pack_start(notebook, True, True, 10)
        
        # Group feedback by item
        item_feedback = {}
        for fb in feedback_data:
            item_id = fb.get("item_id")
            if item_id not in item_feedback:
                item_feedback[item_id] = []
            item_feedback[item_id].append(fb)
        
        # Create a tab for each item
        for item_id, feedback_list in item_feedback.items():
            # Get item name from first feedback entry
            item_name = feedback_list[0].get("item_name", f"Item {item_id}")
            
            # Create tab content
            tab_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            tab_content.set_border_width(10)
            
            # Get menu item to know the components
            menu_item = self.db.get_menu_item(item_id)
            if not menu_item:
                continue
                
            # Calculate average ratings for each component
            component_ratings = {}
            for component in menu_item.get("components", []):
                comp_id = component["id"]
                comp_name = component["name"]
                
                # Initialize count and sum for averaging
                count = 0
                total = 0
                
                # Sum ratings from all feedback
                for fb in feedback_list:
                    rating = fb.get("ratings", {}).get(str(comp_id))
                    if rating:
                        count += 1
                        total += rating
                
                # Calculate average if there are ratings
                if count > 0:
                    avg_rating = total / count
                    component_ratings[comp_id] = {
                        "name": comp_name,
                        "average": avg_rating,
                        "count": count
                    }
            
            # Display component ratings
            for comp_id, data in component_ratings.items():
                comp_frame = Gtk.Frame(label=data["name"])
                tab_content.pack_start(comp_frame, False, False, 5)
                
                comp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                comp_box.set_border_width(10)
                comp_frame.add(comp_box)
                
                # Display average rating
                avg = data["average"]
                rating_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                comp_box.pack_start(rating_box, False, False, 0)
                
                avg_label = Gtk.Label()
                avg_label.set_markup(f"<b>Average Rating:</b> {avg:.2f}/5 (from {data['count']} ratings)")
                avg_label.set_halign(Gtk.Align.START)
                rating_box.pack_start(avg_label, False, False, 0)
                
                # Create a progress bar for visual representation
                progress = Gtk.ProgressBar()
                progress.set_fraction(avg / 5.0)  # Scale to 0-1
                
                # Set color based on rating
                if avg >= 4:
                    color = "success"
                elif avg >= 3:
                    color = "warning"
                else:
                    color = "error"
                    
                progress_context = progress.get_style_context()
                progress_context.add_class(color)
                
                comp_box.pack_start(progress, False, False, 5)
            
            # Create tab label
            tab_label = Gtk.Label(label=item_name)
            notebook.append_page(tab_content, tab_label)
        
        parent_window.show_all()