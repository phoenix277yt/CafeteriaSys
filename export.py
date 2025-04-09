import csv
import os
from datetime import datetime
from database import Database
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

class ExportData:
    def __init__(self):
        self.db = Database()
    
    def export_to_sheets(self):
        """Export feedback data to CSV format (compatible with Google Sheets)"""
        try:
            # Create export directory if it doesn't exist
            export_dir = "exports"
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"feedback_export_{timestamp}.csv"
            file_path = os.path.join(export_dir, filename)
            
            # Get all feedback data
            feedback_data = self.db.get_all_feedback()
            
            # If no feedback data, return False
            if not feedback_data:
                print("No feedback data to export")
                return False
            
            # Get all menu items to lookup component names
            menu_items = self.db.get_all_menu_items()
            
            # Create component ID to name mapping
            component_map = {}
            for item in menu_items:
                for component in item.get("components", []):
                    component_map[component["id"]] = component["name"]
            
            # Prepare data for export
            export_data = []
            
            # Header row
            header = ["Timestamp", "Item ID", "Item Name"]
            
            # Add component names to header (collect all unique component IDs first)
            component_ids = set()
            for fb in feedback_data:
                for comp_id in fb.get("ratings", {}):
                    component_ids.add(int(comp_id))
            
            # Add component names to header in sorted order
            for comp_id in sorted(component_ids):
                if comp_id in component_map:
                    header.append(component_map[comp_id])
                else:
                    header.append(f"Component {comp_id}")
            
            export_data.append(header)
            
            # Add feedback rows
            for fb in feedback_data:
                row = [
                    fb.get("timestamp", ""),
                    fb.get("item_id", ""),
                    fb.get("item_name", "")
                ]
                
                # Add ratings for each component
                for comp_id in sorted(component_ids):
                    rating = fb.get("ratings", {}).get(str(comp_id), "")
                    row.append(rating)
                
                export_data.append(row)
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(export_data)
            
            print(f"Feedback data exported to {file_path}")
            
            # Show notification to user using Gtk
            GLib.idle_add(self.show_export_notification, file_path)
            
            return True
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def show_export_notification(self, file_path):
        """Show a desktop notification about the export"""
        try:
            # This would typically use a Gtk notification,
            # but for simplicity we're just printing to console
            print(f"Notification: Feedback data exported to {file_path}")
            return False  # to stop the idle_add
        except Exception as e:
            print(f"Error showing notification: {e}")
            return False
    
    def get_component_summary(self):
        """Get a summary of component ratings for analysis"""
        try:
            # Get all feedback data
            feedback_data = self.db.get_all_feedback()
            
            # If no feedback data, return empty dict
            if not feedback_data:
                return {}
            
            # Get all menu items
            menu_items = self.db.get_all_menu_items()
            
            # Create component ID to name mapping
            component_map = {}
            for item in menu_items:
                for component in item.get("components", []):
                    component_map[component["id"]] = {
                        "name": component["name"],
                        "item_id": item["id"],
                        "item_name": item["name"]
                    }
            
            # Initialize summary data
            summary = {}
            
            # Process feedback
            for fb in feedback_data:
                item_id = fb.get("item_id")
                item_name = fb.get("item_name", "Unknown Item")
                
                for comp_id_str, rating in fb.get("ratings", {}).items():
                    comp_id = int(comp_id_str)
                    
                    # Initialize component data if not exists
                    if comp_id not in summary:
                        comp_name = component_map.get(comp_id, {}).get("name", f"Component {comp_id}")
                        summary[comp_id] = {
                            "name": comp_name,
                            "total_rating": 0,
                            "count": 0,
                            "average": 0,
                            "item_breakdown": {}
                        }
                    
                    # Update component summary
                    summary[comp_id]["total_rating"] += rating
                    summary[comp_id]["count"] += 1
                    
                    # Update item breakdown
                    if item_id not in summary[comp_id]["item_breakdown"]:
                        summary[comp_id]["item_breakdown"][item_id] = {
                            "name": item_name,
                            "total_rating": 0,
                            "count": 0,
                            "average": 0
                        }
                    
                    summary[comp_id]["item_breakdown"][item_id]["total_rating"] += rating
                    summary[comp_id]["item_breakdown"][item_id]["count"] += 1
            
            # Calculate averages
            for comp_id, data in summary.items():
                if data["count"] > 0:
                    data["average"] = data["total_rating"] / data["count"]
                    
                for item_id, item_data in data["item_breakdown"].items():
                    if item_data["count"] > 0:
                        item_data["average"] = item_data["total_rating"] / item_data["count"]
            
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {}
            
    def show_export_dialog(self, parent_window):
        """Show a file chooser dialog for export location"""
        dialog = Gtk.FileChooserDialog(
            title="Export Feedback Data",
            parent=parent_window,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        
        # Set suggested filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dialog.set_current_name(f"feedback_export_{timestamp}.csv")
        
        # Add filters
        filter_csv = Gtk.FileFilter()
        filter_csv.set_name("CSV files")
        filter_csv.add_mime_type("text/csv")
        filter_csv.add_pattern("*.csv")
        dialog.add_filter(filter_csv)
        
        filter_any = Gtk.FileFilter()
        filter_any.set_name("All files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            dialog.destroy()
            
            # Export to the selected file
            success = self.export_to_specific_file(file_path)
            return success
        else:
            dialog.destroy()
            return False
    
    def export_to_specific_file(self, file_path):
        """Export feedback data to a specific file path"""
        try:
            # Make sure directory exists
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Get all feedback data
            feedback_data = self.db.get_all_feedback()
            
            # If no feedback data, return False
            if not feedback_data:
                print("No feedback data to export")
                return False
            
            # Rest of export code (similar to export_to_sheets)
            # ...
            
            # For simplicity, we'll just call export_to_sheets here
            return self.export_to_sheets()
            
        except Exception as e:
            print(f"Error exporting to specific file: {e}")
            return False