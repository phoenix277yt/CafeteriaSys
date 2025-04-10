# Cafeteria Management System

A simple yet powerful Python-based system for cafeteria management with a focus on component-level feedback collection, built with GTK.

## Features

1. **Component-Level Feedback System**: Users can rate individual components of dishes (e.g., curry, rice, etc.) using a smiley-based rating system.
2. **Menu Display**: View the cafeteria menu with images, dish descriptions, and their individual components.
3. **Date-Based Menu**: See which dishes will be served on specific dates.
4. **Feedback Export**: Administrators can export feedback data to CSV format (compatible with Google Sheets).
5. **Feedback Analysis**: View feedback summaries and average ratings for each dish component.
6. **Advanced Data Analytics**: Comprehensive data analysis with statistical summaries, visualizations, and exportable reports using pandas, numpy, and matplotlib.

## Requirements

- Python 3.6 or higher
- GTK 3.0 and PyGObject
- Pillow (PIL) library for image handling
- pandas for data analysis
- numpy for numerical operations
- matplotlib for visualization

## Installation

### System Dependencies

First, install the required system dependencies:

```bash
# For Debian/Ubuntu/elementaryOS
sudo apt install python3-dev python3-venv python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### Python Environment Setup

This project uses PyGObject (GTK) libraries which are typically installed at the system level. Use one of the following approaches:

#### Option 1: Use a virtual environment with system packages (Recommended)

```bash
# Create a virtual environment with access to system packages
python3 -m venv .venv --system-site-packages

# Activate the virtual environment
source .venv/bin/activate   # For bash/zsh
# OR
source .venv/bin/activate.fish   # For fish shell
# OR
source .venv/bin/activate.csh   # For csh/tcsh

# Install Python dependencies
pip install pillow pandas numpy matplotlib pygobject
```

#### Option 2: Use the system Python directly

If you prefer not to use a virtual environment, you can install the dependencies directly:

```bash
pip3 install --user pillow pandas numpy matplotlib pygobject
```

Note: The `--system-site-packages` flag is crucial as PyGObject (GTK) bindings require system libraries and won't work in an isolated virtual environment.

## File Structure

- `main.py` - Main application entry point
- `database.py` - Handles data storage and retrieval
- `menu.py` - Menu display module
- `feedback.py` - Handles the feedback collection system
- `export.py` - Handles exporting feedback data to CSV
- `analytics.py` - Advanced data analysis and visualization module

## Getting Started

1. Ensure you have all the required dependencies installed (see Installation section)
2. Activate your virtual environment if you're using one
3. Run the application:

```bash
python main.py
```

4. The application will create the necessary directories if they don't exist.

## Usage

### For Users

1. **View Menu**: The "Menu" tab shows available dishes for each date.
2. **Provide Feedback**: 
   - Go to the "Feedback" tab
   - Select a dish from the dropdown
   - Rate each component using the smiley faces
   - Click "Submit Feedback" when done

### For Administrators

1. **View Feedback Summary**: 
   - Go to the "Admin" tab
   - Click "View Feedback Summary" to see feedback statistics
   
2. **Export Feedback**: 
   - Go to the "Admin" tab
   - Click "Export Feedback to Google Sheets"
   - A CSV file will be created in the "exports" folder
   - This file can be imported into Google Sheets
   
3. **Advanced Analytics**:
   - Go to the "Admin" tab
   - Click "Advanced Data Analysis" to open the analytics dashboard
   - View statistical summaries and visualizations across different tabs
   - Click "Export Report" to save all analytics as files

4. **Generate Reports**:
   - Go to the "Admin" tab
   - Click "Generate Analytics Report"
   - Reports will be saved in the "reports" directory with:
     - CSV summary of component statistics
     - Bar charts of component ratings
     - Time series trends of ratings
     - Distribution histograms
     - Heatmaps of item-component ratings

## Design Principles

The application follows :

- Clean, simple interface with appropriate spacing
- Consistent visual hierarchy with proper headings
- Card-based design for menu items
- Native GTK dialogs for interactions
- Clear, readable typography
- Responsive feedback for user actions

## Data Analysis Capabilities

The analytics module provides several data analysis features:

1. **Statistical Summaries**: View counts, means, medians, standard deviations, minimums, and maximums for all component ratings.

2. **Visualizations**:
   - Bar charts showing average ratings for each component with error bars
   - Time series plots showing rating trends over time
   - Histograms displaying the distribution of all ratings
   - Heatmaps showing the relationship between items and their component ratings

3. **Data Export**: Export all analysis results and visualizations as CSV files and PNG images.

## Customizing the Menu

To add or modify menu items, you can edit the `data/menu.json` file that's created after the first run. Each menu item has:
- An ID
- A name
- Image filename (images should be placed in the `images` folder)
- List of components
- Dates on which the dish will be served
