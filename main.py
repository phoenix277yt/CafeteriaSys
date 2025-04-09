import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk
import os
from menu import MenuDisplay
from feedback import FeedbackSystem
from export import ExportData
from analytics import FeedbackAnalytics

class CafeteriaManagementSystem(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Cafeteria Management System")
        self.set_default_size(800, 600)
        self.set_border_width(10)
        
        # Apply elementary OS styling
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)
        self.set_icon_name("applications-utilities")  # Use system icon
        
        # Create CSS provider for styling
        css_provider = Gtk.CssProvider()
        css = b"""
            .main-header {
                font-weight: bold;
                font-size: 18px;
            }
            .sub-header {
                font-weight: bold;
                font-size: 16px;
            }
            .card {
                background: white;
                border: 1px solid #d4d4d4;
                border-radius: 4px;
                padding: 12px;
                margin: 8px;
            }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), 
            css_provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Create a vertical box for main layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.main_box)
        
        # Create header
        header = Gtk.Label(label="Cafeteria Management System")
        context = header.get_style_context()
        context.add_class("main-header")
        header.set_margin_bottom(10)
        self.main_box.pack_start(header, False, False, 0)
        
        # Create notebook (tabbed interface)
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        self.main_box.pack_start(self.notebook, True, True, 0)
        
        # Menu Tab
        self.menu_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.menu_display = MenuDisplay(self.menu_tab)
        menu_label = Gtk.Label(label="Menu")
        self.notebook.append_page(self.menu_tab, menu_label)
        
        # Feedback Tab
        self.feedback_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.feedback_system = FeedbackSystem(self.feedback_tab)
        feedback_label = Gtk.Label(label="Feedback")
        self.notebook.append_page(self.feedback_tab, feedback_label)
        
        # Admin Tab
        self.admin_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        admin_label = Gtk.Label(label="Admin")
        self.notebook.append_page(self.admin_tab, admin_label)
        self.create_admin_panel()
    
    def create_admin_panel(self):
        # Create a box for admin content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_bottom(10)
        self.admin_tab.pack_start(box, True, True, 0)
        
        # Admin title
        admin_title = Gtk.Label(label="Admin Panel")
        context = admin_title.get_style_context()
        context.add_class("sub-header")
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
    
    def export_feedback(self, button):
        exporter = ExportData()
        success = exporter.export_to_sheets()
        
        if success:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Export Successful",
            )
            dialog.format_secondary_text("Feedback data exported to Google Sheets format successfully!")
        else:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Export Failed",
            )
            dialog.format_secondary_text("Failed to export data. Check console for details.")
        
        dialog.run()
        dialog.destroy()
    
    def view_feedback_summary(self, button):
        feedback_window = Gtk.Window(title="Feedback Summary")
        feedback_window.set_default_size(600, 400)
        feedback_window.set_transient_for(self)
        feedback_window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        
        # This would display a summary of the feedback
        self.feedback_system.display_summary(feedback_window)
        
        feedback_window.show_all()
    
    def show_data_analysis(self, button):
        """Show the data analysis dialog"""
        analytics = FeedbackAnalytics()
        analytics.show_analysis(self)
    
    def generate_report(self, button):
        """Generate a comprehensive analytics report"""
        analytics = FeedbackAnalytics()
        report_path = analytics.save_report()
        
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Report Generated",
        )
        dialog.format_secondary_text(f"Analytics report has been saved to {report_path}")
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("images"):
        os.makedirs("images")
        
    win = CafeteriaManagementSystem()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()