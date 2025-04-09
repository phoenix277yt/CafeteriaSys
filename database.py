import json
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.menu_file = "data/menu.json"
        self.feedback_file = "data/feedback.json"
        self._init_files()
    
    def _init_files(self):
        """Initialize data files if they don't exist"""
        if not os.path.exists(self.menu_file):
            with open(self.menu_file, 'w') as f:
                json.dump({
                    "menu_items": [
                        {
                            "id": 1,
                            "name": "Curry Chawal",
                            "image": "curry_chawal.jpg",
                            "components": [
                                {"id": 1, "name": "Curry"},
                                {"id": 2, "name": "Rice"},
                                {"id": 3, "name": "Pakoda"}
                            ],
                            "dates_served": ["2023-06-01", "2023-06-08", "2023-06-15"]
                        },
                        {
                            "id": 2,
                            "name": "Dal Khichdi",
                            "image": "dal_khichdi.jpg",
                            "components": [
                                {"id": 4, "name": "Dal"},
                                {"id": 5, "name": "Rice"},
                                {"id": 6, "name": "Ghee"}
                            ],
                            "dates_served": ["2023-06-02", "2023-06-09", "2023-06-16"]
                        }
                    ]
                }, f, indent=4)
        
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w') as f:
                json.dump({
                    "feedback": []
                }, f, indent=4)
    
    def get_all_menu_items(self):
        """Retrieve all menu items"""
        try:
            with open(self.menu_file, 'r') as f:
                data = json.load(f)
                return data.get("menu_items", [])
        except Exception as e:
            print(f"Error loading menu data: {e}")
            return []
    
    def get_menu_item(self, item_id):
        """Get a specific menu item by ID"""
        items = self.get_all_menu_items()
        for item in items:
            if item["id"] == item_id:
                return item
        return None
    
    def add_feedback(self, feedback_data):
        """Add new feedback entry"""
        try:
            with open(self.feedback_file, 'r') as f:
                data = json.load(f)
            
            # Add timestamp to feedback
            feedback_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["feedback"].append(feedback_data)
            
            with open(self.feedback_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    def get_all_feedback(self):
        """Retrieve all feedback data"""
        try:
            with open(self.feedback_file, 'r') as f:
                data = json.load(f)
                return data.get("feedback", [])
        except Exception as e:
            print(f"Error loading feedback data: {e}")
            return []
    
    def get_feedback_for_item(self, item_id):
        """Get feedback specific to a menu item"""
        all_feedback = self.get_all_feedback()
        return [fb for fb in all_feedback if fb.get("item_id") == item_id]