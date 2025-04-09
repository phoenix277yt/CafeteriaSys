import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from database import Database
import os
from datetime import datetime, timedelta

class FeedbackAnalytics:
    def __init__(self):
        self.db = Database()
        
    def load_feedback_data(self):
        """Load feedback data into pandas DataFrame"""
        feedback_data = self.db.get_all_feedback()
        if not feedback_data:
            return pd.DataFrame()
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(feedback_data)
        
        # Process timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            
        # Extract ratings into separate columns
        if 'ratings' in df.columns:
            # Get all component IDs
            component_ids = set()
            for ratings in df['ratings']:
                component_ids.update(ratings.keys())
                
            # Create columns for each component rating
            for comp_id in component_ids:
                df[f'rating_{comp_id}'] = df['ratings'].apply(
                    lambda x: x.get(str(comp_id), np.nan)
                )
                
        return df
        
    def get_components_summary(self):
        """Get statistical summary of component ratings"""
        df = self.load_feedback_data()
        if df.empty:
            return pd.DataFrame()
            
        # Get columns that contain ratings
        rating_cols = [col for col in df.columns if col.startswith('rating_')]
        
        if not rating_cols:
            return pd.DataFrame()
            
        # Create a summary DataFrame
        summary = pd.DataFrame()
        menu_items = self.db.get_all_menu_items()
        
        # Build component ID to name mapping
        comp_mapping = {}
        for item in menu_items:
            for comp in item.get('components', []):
                comp_mapping[f"rating_{comp['id']}"] = comp['name']
        
        # Calculate statistics for each component
        for col in rating_cols:
            comp_name = comp_mapping.get(col, col)
            
            # Skip if no ratings
            if df[col].isna().all():
                continue
                
            stats = {
                'Component': comp_name,
                'Count': df[col].count(),
                'Mean': df[col].mean(),
                'Median': df[col].median(),
                'Std Dev': df[col].std(),
                'Min': df[col].min(),
                'Max': df[col].max()
            }
            
            summary = pd.concat([summary, pd.DataFrame([stats])], ignore_index=True)
            
        return summary
    
    def generate_component_ratings_plot(self):
        """Generate bar plot of average component ratings"""
        summary = self.get_components_summary()
        
        if summary.empty:
            return None
            
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create bar chart
        bars = ax.bar(summary['Component'], summary['Mean'], yerr=summary['Std Dev'], 
                     capsize=5, color='skyblue', edgecolor='black')
        
        # Add rating values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{height:.2f}', ha='center', va='bottom')
        
        # Customize plot
        ax.set_xlabel('Component')
        ax.set_ylabel('Average Rating')
        ax.set_title('Average Component Ratings')
        ax.set_ylim(0, 5.5)  # Ratings are from 1-5
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Rotate x labels if there are many components
        if len(summary) > 4:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        return fig
    
    def generate_time_series_plot(self):
        """Generate time series plot of ratings over time"""
        df = self.load_feedback_data()
        
        if df.empty or 'date' not in df.columns:
            return None
            
        # Get rating columns
        rating_cols = [col for col in df.columns if col.startswith('rating_')]
        
        if not rating_cols:
            return None
            
        # Create component ID to name mapping
        menu_items = self.db.get_all_menu_items()
        comp_mapping = {}
        for item in menu_items:
            for comp in item.get('components', []):
                comp_mapping[f"rating_{comp['id']}"] = comp['name']
        
        # Group by date and calculate mean for each component
        daily_ratings = df.groupby('date')[rating_cols].mean().reset_index()
        
        # Handle dates with no data by creating a complete date range
        if len(daily_ratings) > 1:
            date_range = pd.date_range(start=daily_ratings['date'].min(), 
                                      end=daily_ratings['date'].max())
            daily_ratings = daily_ratings.set_index('date').reindex(date_range).reset_index()
            daily_ratings = daily_ratings.rename(columns={'index': 'date'})
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot each component as a line
        for col in rating_cols:
            if col in daily_ratings.columns:
                comp_name = comp_mapping.get(col, col)
                ax.plot(daily_ratings['date'], daily_ratings[col], 
                       marker='o', linestyle='-', label=comp_name)
        
        # Customize plot
        ax.set_xlabel('Date')
        ax.set_ylabel('Average Rating')
        ax.set_title('Rating Trends Over Time')
        ax.set_ylim(0, 5.5)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        plt.tight_layout()
        return fig
    
    def generate_histogram(self):
        """Generate histogram of all ratings"""
        df = self.load_feedback_data()
        
        if df.empty:
            return None
            
        # Get rating columns
        rating_cols = [col for col in df.columns if col.startswith('rating_')]
        
        if not rating_cols:
            return None
            
        # Get all ratings as a flat list
        all_ratings = []
        for col in rating_cols:
            all_ratings.extend(df[col].dropna().tolist())
            
        if not all_ratings:
            return None
            
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create histogram
        bins = np.arange(0.5, 6.5, 1)  # Bins for ratings 1-5
        n, bins, patches = ax.hist(all_ratings, bins=bins, 
                                  color='skyblue', edgecolor='black', alpha=0.7)
        
        # Add count labels
        for i, patch in enumerate(patches):
            height = patch.get_height()
            if height > 0:
                ax.text(patch.get_x() + patch.get_width()/2., height + 0.1,
                       int(height), ha='center', va='bottom')
        
        # Customize plot
        ax.set_xlabel('Rating')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of Ratings')
        ax.set_xticks(range(1, 6))
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
        
    def generate_heatmap(self):
        """Generate heatmap of component ratings by item"""
        df = self.load_feedback_data()
        
        if df.empty:
            return None
            
        # Get rating columns
        rating_cols = [col for col in df.columns if col.startswith('rating_')]
        
        if not rating_cols or 'item_name' not in df.columns:
            return None
            
        # Group by item and calculate mean for each component
        item_component_ratings = df.groupby('item_name')[rating_cols].mean()
        
        # Return None if no data
        if item_component_ratings.empty:
            return None
            
        # Create component ID to name mapping
        menu_items = self.db.get_all_menu_items()
        comp_mapping = {}
        for item in menu_items:
            for comp in item.get('components', []):
                comp_mapping[f"rating_{comp['id']}"] = comp['name']
                
        # Rename columns to component names
        item_component_ratings = item_component_ratings.rename(columns=comp_mapping)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create heatmap
        im = ax.imshow(item_component_ratings, cmap='YlGn', aspect='auto')
        
        # Customize plot
        ax.set_xlabel('Component')
        ax.set_ylabel('Item')
        ax.set_title('Average Ratings by Item and Component')
        
        # Set x and y ticks
        ax.set_xticks(np.arange(len(item_component_ratings.columns)))
        ax.set_yticks(np.arange(len(item_component_ratings.index)))
        ax.set_xticklabels(item_component_ratings.columns)
        ax.set_yticklabels(item_component_ratings.index)
        
        # Rotate x labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.set_label('Average Rating')
        
        # Add text annotations
        for i in range(len(item_component_ratings.index)):
            for j in range(len(item_component_ratings.columns)):
                text = ax.text(j, i, f"{item_component_ratings.iloc[i, j]:.2f}",
                              ha="center", va="center", color="black")
        
        plt.tight_layout()
        return fig
    
    def save_report(self, output_dir="reports"):
        """Save analytics report to file"""
        # Create reports directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"feedback_report_{timestamp}"
        
        # Save summary to CSV
        summary = self.get_components_summary()
        if not summary.empty:
            summary.to_csv(f"{output_dir}/{filename}_summary.csv", index=False)
            
        # Save plots
        plots = {
            "ratings_bar": self.generate_component_ratings_plot(),
            "time_series": self.generate_time_series_plot(),
            "histogram": self.generate_histogram(),
            "heatmap": self.generate_heatmap()
        }
        
        for name, fig in plots.items():
            if fig:
                fig.savefig(f"{output_dir}/{filename}_{name}.png", dpi=100)
                plt.close(fig)
                
        return f"{output_dir}/{filename}"
    
    def show_analysis(self, parent_window):
        """Show analysis in GTK window"""
        # Create window
        dialog = Gtk.Dialog(
            title="Feedback Analysis",
            parent=parent_window,
            flags=0,
            buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        )
        dialog.set_default_size(800, 600)
        
        # Create notebook for tabs
        notebook = Gtk.Notebook()
        dialog.get_content_area().pack_start(notebook, True, True, 0)
        
        # Summary tab
        summary_frame = Gtk.Frame(label="Statistical Summary")
        summary_scroll = Gtk.ScrolledWindow()
        summary_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        summary_frame.add(summary_scroll)
        
        summary = self.get_components_summary()
        if not summary.empty:
            # Create a grid to display summary data
            grid = Gtk.Grid()
            grid.set_border_width(10)
            grid.set_column_spacing(15)
            grid.set_row_spacing(5)
            summary_scroll.add(grid)
            
            # Add headers
            headers = ['Component', 'Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max']
            for i, header in enumerate(headers):
                label = Gtk.Label(label=f"<b>{header}</b>")
                label.set_use_markup(True)
                grid.attach(label, i, 0, 1, 1)
                
            # Add data rows
            for row_idx, (_, row) in enumerate(summary.iterrows(), 1):
                for col_idx, col in enumerate(headers):
                    value = row[col]
                    if isinstance(value, (int, np.integer)):
                        text = str(value)
                    elif isinstance(value, (float, np.float64)):
                        text = f"{value:.2f}"
                    else:
                        text = str(value)
                    
                    label = Gtk.Label(label=text)
                    label.set_halign(Gtk.Align.START)
                    grid.attach(label, col_idx, row_idx, 1, 1)
        else:
            label = Gtk.Label(label="No feedback data available for analysis.")
            summary_scroll.add(label)
            
        notebook.append_page(summary_frame, Gtk.Label(label="Summary"))
        
        # Component ratings plot tab
        ratings_plot = self.generate_component_ratings_plot()
        if ratings_plot:
            canvas = FigureCanvas(ratings_plot)
            canvas.set_size_request(700, 400)
            notebook.append_page(canvas, Gtk.Label(label="Component Ratings"))
        
        # Time series plot tab
        time_series_plot = self.generate_time_series_plot()
        if time_series_plot:
            canvas = FigureCanvas(time_series_plot)
            canvas.set_size_request(700, 400)
            notebook.append_page(canvas, Gtk.Label(label="Rating Trends"))
        
        # Histogram tab
        histogram_plot = self.generate_histogram()
        if histogram_plot:
            canvas = FigureCanvas(histogram_plot)
            canvas.set_size_request(700, 400)
            notebook.append_page(canvas, Gtk.Label(label="Rating Distribution"))
            
        # Heatmap tab
        heatmap_plot = self.generate_heatmap()
        if heatmap_plot:
            canvas = FigureCanvas(heatmap_plot)
            canvas.set_size_request(700, 400)
            notebook.append_page(canvas, Gtk.Label(label="Item-Component Heatmap"))
        
        # Add export button
        export_button = Gtk.Button(label="Export Report")
        export_button.connect("clicked", self._on_export_clicked, dialog)
        action_area = dialog.get_action_area()
        action_area.pack_start(export_button, False, False, 0)
        action_area.set_layout(Gtk.ButtonBoxStyle.END)
        
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
    
    def _on_export_clicked(self, button, parent_dialog):
        """Handler for export button click"""
        report_path = self.save_report()
        
        dialog = Gtk.MessageDialog(
            transient_for=parent_dialog,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Report Exported",
        )
        dialog.format_secondary_text(f"Report exported to {report_path}")
        dialog.run()
        dialog.destroy()