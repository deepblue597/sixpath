# SixPaths - Professional Networking Visualization

🔗 **SixPaths** is a comprehensive Streamlit web application for visualizing and managing your professional network. Track connections, manage referrals, and see your network come to life with interactive visualizations.

## Features

### 🔐 Authentication

- Secure login system with session management
- Guest login for quick demo access
- Demo credentials: `demo` / `password`

### 📊 Interactive Dashboard

- **Network Visualization**: Interactive graph powered by pyvis
  - Central node represents you
  - Surrounding nodes represent connections
  - Color-coded by sector or company
  - Node size reflects relationship strength
  - Click nodes to edit connections
- **Filters**: Filter by sector, company
- **Metrics**: View total connections, sectors, recent interactions
- **Searchable Table**: Quick search through all connections

### 🎯 Referrals Management

- Track incoming job referrals from your network
- Search and filter by sector, company, status
- Table and card views
- Action buttons: View, Edit, Delete
- Export to CSV
- Status tracking: Pending, Interview Scheduled, Applied, etc.

### 👤 Profile Management

- Edit your professional information
- Update name, company, sector, contact details
- View profile statistics
- LinkedIn integration

### ✏️ Connection Management

- Add new connections
- Edit existing connections
- Delete connections
- Track relationship details:
  - How you know them
  - Last interaction date
  - Relationship strength (1-10)
  - Notes and context
- Quick actions: View in network, check referrals

## Technology Stack

- **Streamlit**: Web framework
- **Pyvis**: Interactive network visualization
- **Pandas**: Data manipulation
- **NetworkX**: Graph algorithms (foundation for pyvis)

## Installation

```bash
# Install dependencies
uv add streamlit pyvis pandas networkx

# Or using pip
pip install streamlit pyvis pandas networkx
```

## Running the Application

```bash
# Run with Streamlit
streamlit run streamlit_app.py

# Or with uv
uv run streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

## Project Structure

```
sixpath/
├── streamlit_app.py          # Main entry point
├── pages/
│   ├── 01_Login.py           # Authentication page
│   ├── 02_Dashboard.py       # Network visualization
│   ├── 03_Referrals.py       # Referrals management
│   ├── 04_Edit_Profile.py    # User profile editing
│   └── 05_Edit_Connection.py # Connection editing
├── utils/
│   ├── mock_data.py          # Sample data generator
│   └── styling.py            # Custom CSS styling
└── README_STREAMLIT.md       # This file
```

## Usage Guide

### Getting Started

1. **Login**: Use demo/password or click "Guest Login"
2. **Explore Dashboard**: View your network visualization
3. **Navigate**: Use sidebar or quick action buttons
4. **Interact**: Click network nodes to edit connections

### Dashboard Features

- **Color Coding**: Choose between sector-based or company-based colors
- **Physics**: Toggle force-directed layout on/off
- **Labels**: Show/hide node labels
- **Filters**: Select which sectors and companies to display
- **Zoom**: Use mouse wheel to zoom in/out
- **Pan**: Click and drag to move around

### Managing Connections

1. Click any node in the dashboard OR
2. Click "Add Connection" button
3. Fill in connection details
4. Save changes

### Managing Referrals

1. Navigate to Referrals page
2. Search and filter referrals
3. Click "View Referrer" to see connection details
4. Track status updates
5. Export data to CSV

## Design

### Color Scheme

- **Primary Navy**: `#1E3A8A`
- **Secondary Blue**: `#3B82F6`
- **Accent Gold**: `#F59E0B`
- **Background**: `#F8FAFC`

### Sector Colors

- Technology: Blue (`#3B82F6`)
- Finance: Green (`#10B981`)
- Healthcare: Red (`#EF4444`)
- Education: Amber (`#F59E0B`)
- Marketing: Purple (`#8B5CF6`)
- Manufacturing: Gray (`#6B7280`)

## Mock Data

The application generates sample data on login:

- 25 random professional connections
- 8 sample referrals
- Connections across 6 industry sectors
- Various relationship strengths and interaction dates

## Future Enhancements

Potential features to add:

- [ ] Database integration (replace mock data)
- [ ] Export network as image
- [ ] Email notifications for referral updates
- [ ] Calendar integration for tracking interactions
- [ ] Advanced analytics and insights
- [ ] Import contacts from LinkedIn
- [ ] Collaboration features (share networks)
- [ ] Mobile app version

## Customization

### Adding New Sectors

Edit `utils/mock_data.py`:

```python
SECTORS = [
    "Technology",
    "Finance",
    "Your New Sector"
]
```

### Changing Colors

Edit `utils/styling.py` to modify the CSS theme.

### Adjusting Network Layout

Edit `pages/02_Dashboard.py` to modify pyvis settings:

```python
net.set_options("""
{
    "physics": {
        "forceAtlas2Based": {
            "gravitationalConstant": -50,
            "springLength": 200
        }
    }
}
""")
```

## Troubleshooting

### Network not rendering

- Check browser console for errors
- Try disabling browser extensions
- Refresh the page

### Data not persisting

- This is a demo using session state
- Data resets on logout or page refresh
- For persistence, integrate a database

### Performance issues

- Reduce number of connections
- Disable physics simulation
- Hide node labels

## License

This is a demonstration project. Feel free to use and modify for your needs.

## Credits

Built with ❤️ using:

- [Streamlit](https://streamlit.io/)
- [Pyvis](https://pyvis.readthedocs.io/)
- [Pandas](https://pandas.pydata.org/)

---

**SixPaths** © 2026 | Professional Networking Made Visual
