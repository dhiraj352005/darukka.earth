import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import MapView from './MapView'
import SiteAnalytics from './SiteAnalytics'
import './Dashboard.css'

const Dashboard = () => {
  const { user, logout } = useAuth()
  const [selectedSite, setSelectedSite] = useState(null)
  const [showAnalytics, setShowAnalytics] = useState(false)
  
  // Check if user is admin (adjust based on your user object structure)
  const isAdmin = user?.is_admin || user?.isAdmin || false

  const handleLogout = () => {
    logout()
    // User state will be cleared and App.jsx will show Login
  }

  const handleSiteClick = (siteProperties) => {
    console.log('Site clicked:', siteProperties)
    setSelectedSite(siteProperties)
    setShowAnalytics(true)
  }

  const closeAnalytics = () => {
    setShowAnalytics(false)
    setSelectedSite(null)
  }

  // Get user initials for avatar
  const getUserInitials = () => {
    if (user?.name) {
      return user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    }
    return user?.email?.slice(0, 2).toUpperCase() || 'U'
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🌍 Darukaa.Earth</h1>
          <span className="header-subtitle">Climate Tech Platform</span>
        </div>
        <div className="header-right">
          <div className="user-info">
            <div className="user-avatar">{getUserInitials()}</div>
            <div className="user-details">
              <span className="user-name">
                {user?.name || user?.email}
                {isAdmin && <span className="admin-badge">Admin</span>}
              </span>
              <span className="user-email">{user?.email}</span>
            </div>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <MapView onSiteClick={handleSiteClick} isAdmin={isAdmin} />
      </div>

      {showAnalytics && selectedSite && (
        <SiteAnalytics site={selectedSite} onClose={closeAnalytics} />
      )}
    </div>
  )
}

export default Dashboard
