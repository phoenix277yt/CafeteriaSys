import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk

from menu import MenuDisplay, MenuSystem
from feedback import FeedbackSystem
from export import ExportData
from analytics import FeedbackAnalytics
from theme_manager import ThemeManager
from database import Database

class CafeteriaManagementSystem(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Cafeteria Management System")
        self.set_default_size(800, 600)
        self.set_border_width(10)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Initialize database and systems first
        self.db = Database()
        self.menu_system = MenuSystem()
        self.export_data = ExportData()
        self.analytics = FeedbackAnalytics()
        
        # Apply elementary OS styling
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)
        self.set_icon_name("applications-utilities")  # Use system icon
        
        # Create a vertical box for main layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.main_box)
        
        # Create header
        self.create_header()
        
        # Create notebook (tabbed interface)
        self.notebook = Gtk.Notebook()
        self.main_box.pack_start(self.notebook, True, True, 0)
        
        # Create tabs
        self.menu_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.feedback_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.admin_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        self.notebook.append_page(self.menu_tab, Gtk.Label(label="Menu"))
        self.notebook.append_page(self.feedback_tab, Gtk.Label(label="Feedback"))
        self.notebook.append_page(self.admin_tab, Gtk.Label(label="Admin"))
        
        # Initialize menu display with menu_tab as parent
        self.menu_display = MenuDisplay(self.menu_tab)
        
        # Initialize feedback system and pass the feedback_tab to create_feedback_ui
        self.feedback_system = FeedbackSystem(self)
        self.feedback_system.create_feedback_ui(self.feedback_tab)
        
        # Create admin panel
        self.create_admin_panel()
        
        # Apply theme
        self.apply_theme()
        
        self.show_all()
        
    def create_header(self):
        """Create header with title and logo"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_margin_bottom(10)
        
        # Title
        title = Gtk.Label()
        title.set_markup("<span size='x-large' weight='bold'>Cafeteria Management System</span>")
        header_box.pack_start(title, True, True, 0)
        
        self.main_box.pack_start(header_box, False, False, 0)
    
    def create_admin_panel(self):
        """Create admin panel with export and analysis options"""
        # Create a box for admin content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_bottom(10)
        self.admin_tab.pack_start(box, True, True, 0)
        
        # Admin title
        admin_title = Gtk.Label(label="Admin Panel")
        admin_title.set_halign(Gtk.Align.START)  # Left align
        box.pack_start(admin_title, False, False, 10)
        
        # Export button
        export_button = Gtk.Button(label="Export Feedback to Google Sheets")
        export_button.connect("clicked", self.export_feedback)
        box.pack_start(export_button, False, False, 5)
        
        # View feedback summary button
        view_button = Gtk.Button(label="View Feedback Summary")
        view_button.connect("clicked", self.view_feedback_summary)
        box.pack_start(view_button, False, False, 5)
        
        # Add new Data Analysis button
        analysis_button = Gtk.Button(label="Advanced Data Analysis")
        analysis_button.connect("clicked", self.show_data_analysis)
        box.pack_start(analysis_button, False, False, 5)
        
        # Add Save Report button
        report_button = Gtk.Button(label="Generate Analytics Report")
        report_button.connect("clicked", self.generate_report)
        box.pack_start(report_button, False, False, 5)
        
        # Add separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(10)
        separator.set_margin_bottom(10)
        box.pack_start(separator, False, False, 0)
        
        # Add theme selector
        self.theme_manager.create_theme_selector(box)
    
    def export_feedback(self, widget):
        """Export feedback data to Google Sheets format"""
        success = self.export_data.export_to_csv()
        
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Export Complete",
        )
        
        if success:
            dialog.format_secondary_text(
                "Feedback data has been exported successfully to the 'exports' folder."
            )
        else:
            dialog.format_secondary_text(
                "There was a problem exporting the feedback data."
            )
        
        dialog.run()
        dialog.destroy()
    
    def view_feedback_summary(self, widget):
        """Show feedback summary dialog"""
        summary = self.feedback_system.get_feedback_summary()
        
        dialog = Gtk.Dialog(
            title="Feedback Summary",
            transient_for=self,
            flags=0,
            buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        )
        
        dialog.set_default_size(400, 300)
        content_area = dialog.get_content_area()
        
        # Create a scrolled window for the content
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        content_area.pack_start(scrolled_window, True, True, 0)
        
        # Create a box for the content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        content_box.set_margin_top(10)
        content_box.set_margin_start(10)
        content_box.set_margin_end(10)
        content_box.set_margin_bottom(10)
        scrolled_window.add(content_box)
        
        # Add summary content
        if summary:
            for dish_name, components in summary.items():
                dish_label = Gtk.Label()
                dish_label.set_markup(f"<b>{dish_name}</b>")
                dish_label.set_halign(Gtk.Align.START)
                content_box.pack_start(dish_label, False, False, 5)
                
                for component, rating in components.items():
                    component_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                    component_label = Gtk.Label(label=f"{component}:")
                    component_label.set_halign(Gtk.Align.START)
                    component_box.pack_start(component_label, False, False, 5)
                    
                    rating_label = Gtk.Label(label=f"{rating:.1f}/5.0")
                    component_box.pack_start(rating_label, False, False, 0)
                    
                    content_box.pack_start(component_box, False, False, 2)
                
                # Add separator between dishes
                separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                content_box.pack_start(separator, False, False, 10)
        else:
            no_data_label = Gtk.Label(label="No feedback data available.")
            content_box.pack_start(no_data_label, False, False, 0)
        
        dialog.show_all()
        dialog.run()
        dialog.destroy()
    
    def show_data_analysis(self, widget):
        """Show advanced data analysis window"""
        success = self.analytics.show_analysis_window()
        
        if not success:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Analysis Error",
            )
            dialog.format_secondary_text(
                "Could not generate the analysis. There might not be enough feedback data."
            )
            dialog.run()
            dialog.destroy()
    
    def generate_report(self, widget):
        """Generate and save analytics report"""
        success = self.analytics.generate_report()
        
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Report Generation Complete",
        )
        
        if success:
            dialog.format_secondary_text(
                "Analytics report has been generated successfully in the 'reports' folder."
            )
        else:
            dialog.format_secondary_text(
                "There was a problem generating the analytics report."
            )
        
        dialog.run()
        dialog.destroy()
    
    def apply_theme(self):
        """Apply the selected theme"""
        self.theme_manager.apply_theme()

def main():
    win = CafeteriaManagementSystem()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()