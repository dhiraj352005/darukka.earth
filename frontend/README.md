# Darukaa.Earth Frontend

React dashboard for managing restoration and conservation projects with interactive mapping and analytics.

## Features

✅ **JWT Authentication** - Secure login and registration  
✅ **Mapbox GL JS Integration** - Full-screen interactive satellite map  
✅ **Polygon Drawing Tools** - Draw site boundaries directly on the map  
✅ **Site Management** - Save, load, and visualize geographical sites  
✅ **Performance Analytics** - Highcharts-powered data visualization  
✅ **Admin Controls** - Role-based access for site creation  
✅ **Responsive Design** - Works on desktop and mobile  

## Tech Stack

- **React** 18.3.1 - UI framework
- **Vite** 6.0.7 - Build tool
- **Mapbox GL JS** - Interactive maps
- **Mapbox Draw** - Polygon drawing plugin
- **Highcharts** - Data visualization
- **Axios** - HTTP client
- **React Router** - Navigation
- **ESLint** + **Prettier** - Code quality

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
```

### Environment Variables

The `.env` file is already configured with:

```
VITE_MAPBOX_TOKEN=<your-mapbox-token>
VITE_API_URL=http://localhost:8000
```

### Running the App

```bash
npm run dev
```

App will be available at http://localhost:5173

### Building for Production

```bash
npm run build
npm run preview
```

## Application Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.jsx           # Authentication UI
│   │   ├── Dashboard.jsx       # Main dashboard layout
│   │   ├── MapView.jsx         # Mapbox map component
│   │   └── SiteAnalytics.jsx   # Highcharts analytics modal
│   ├── context/
│   │   └── AuthContext.jsx     # Authentication state management
│   ├── services/
│   │   └── api.js              # API client and endpoints
│   ├── App.jsx                 # Router and protected routes
│   └── main.jsx                # Application entry point
├── .env                        # Environment variables
└── package.json
```

## User Guide

### 1. Authentication

**Register:**
- Click "Register" tab
- Enter username, email, password
- Check "Register as Administrator" for admin access
- Click "Register"

**Login:**
- Enter email and password
- Click "Login"
- Redirects to dashboard on success

### 2. Dashboard (All Users)

- View full-screen satellite map
- See all existing project sites as colored polygons
- Click on any site polygon to view analytics
- User info displayed in header
- Logout button in top-right

### 3. Drawing Sites (Admin Only)

**Create New Site:**
1. Click the polygon tool (top-left of map)
2. Click on map to place polygon vertices
3. Double-click to complete polygon
4. Click "💾 Save Site" button
5. Enter site name and project ID
6. Site saves to backend and appears on map

**Controls:**
- **🗑️ Clear** - Remove drawn polygons without saving
- **🔄 Refresh Sites** - Reload sites from backend
- **Trash tool** - Delete individual drawn polygons

### 4. Site Analytics

**View Performance Data:**
1. Click on any site polygon on the map
2. Analytics modal opens showing:
   - **Overview Tab:**
     - Total trees, species count, carbon captured, soil quality
     - Tree growth timeline chart
     - Biodiversity area chart
   - **Detailed Metrics Tab:**
     - Carbon sequestration column chart
     - Soil health spline chart
     - All performance charts in grid layout

**Analytics Features:**
- Interactive Highcharts with zoom and tooltips
- Dummy data for demonstration (real-time integration pending)
- Responsive modal design
- Close button or click outside to dismiss

## API Integration

### Authentication Endpoints

```javascript
POST /auth/register  - Register new user
POST /auth/login     - Login and get JWT token
GET  /auth/me        - Get current user info
```

### Site Management Endpoints (Admin)

```javascript
GET    /sites        - Fetch all sites
POST   /sites        - Create new site
POST   /sites/bulk   - Create multiple sites
GET    /sites/{id}   - Get specific site
DELETE /sites/{id}   - Delete site
```

### Data Format

**Site GeoJSON:**
```json
{
  "name": "Site Alpha",
  "description": "Primary restoration area",
  "project_id": 1,
  "geometry": {
    "type": "Polygon",
    "coordinates": [[
      [77.5946, 12.9716],
      [77.5956, 12.9716],
      [77.5956, 12.9726],
      [77.5946, 12.9726],
      [77.5946, 12.9716]
    ]]
  },
  "area_hectares": 100,
  "location_info": "Near coastal highway"
}
```

## Mapbox Integration

### Token Configuration

Mapbox token is stored in `.env` as `VITE_MAPBOX_TOKEN`.

### Map Features

- **Style:** Satellite Streets (satellite imagery + street labels)
- **Default Center:** Bangalore, India (77.5946, 12.9716)
- **Zoom Level:** 12
- **Controls:** Navigation, Fullscreen

### Drawing Plugin

- **Mapbox Draw** configured for polygon mode
- Admin-only access
- Automatic feature tracking
- GeoJSON output

### Site Visualization

- Existing sites loaded as GeoJSON layer
- Cyan fill color with 40% opacity
- Cyan outline with 2px width
- Clickable polygons
- Cursor changes on hover
- Auto-fit bounds to show all sites

## Component Details

### Login Component

- Tabbed interface (Login/Register)
- Form validation
- Error messaging
- Admin registration option
- Gradient design
- Responsive layout

### Dashboard Component

- Header with branding and user info
- Admin badge display
- Logout functionality
- Full-screen map container
- Analytics modal integration

### MapView Component

- Mapbox GL JS initialization
- Mapbox Draw plugin (admin only)
- Site loading and rendering
- Drawing state management
- Save/Clear/Refresh controls
- Click event handling

### SiteAnalytics Component

- Modal overlay design
- Tabbed analytics view
- Highcharts integration
- Dummy data generation
- Stat cards with metrics
- Responsive charts
- Close on overlay click

## Styling

All components use CSS modules with:
- Gradient purple theme (#667eea to #764ba2)
- Consistent border radius (8-12px)
- Box shadows for depth
- Smooth transitions
- Responsive breakpoints
- Accessibility-friendly colors

## Development

### Running with Backend

1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:5173

### Pre-commit Hooks

Husky and lint-staged automatically:
- Format code with Prettier
- Lint code with ESLint
- Run on every commit

### Common Commands

```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

## Troubleshooting

### Mapbox Not Loading

- Check VITE_MAPBOX_TOKEN in .env
- Verify token is valid
- Check browser console for errors

### API Connection Issues

- Ensure backend is running on port 8000
- Check VITE_API_URL in .env
- Verify CORS is configured in backend

### Sites Not Displaying

- Check authentication (must be logged in)
- Verify backend has sites in database
- Open browser console for errors
- Try "Refresh Sites" button

### Drawing Not Working

- Ensure user is registered as admin
- Check admin badge in dashboard header
- Verify Mapbox Draw plugin loaded
- Look for console errors

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Lazy loading for analytics
- Optimized map rendering
- Efficient GeoJSON processing
- Minimal re-renders
- Production build minification

## Security

- JWT tokens in localStorage
- Automatic token refresh
- Protected routes
- Admin role verification
- Secure API communication

## Future Enhancements

- [ ] Real-time analytics data
- [ ] Multi-project support
- [ ] Advanced filtering
- [ ] Export functionality
- [ ] Offline mode
- [ ] Mobile app
- [ ] 3D terrain view
- [ ] Time-series playback

## License

Part of the Darukaa.Earth project.
