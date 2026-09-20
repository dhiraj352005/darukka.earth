import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import MapView from './MapView'
import SiteAnalytics from './SiteAnalytics'
import './Dashboard.css'

const Dashboard = () => {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()
  const [selectedSite, setSelectedSite] = useState(null)
  const [showAnalytics, setShowAnalytics] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
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
    if (user?.full_name) {
      return user.full_name.split(' ').map(n => n[0]).join('').slice(0, 2)
    }
    return user?.username?.slice(0, 2) || 'U'
  }

  return (
    <div className="dashboard">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'white',
            color: 'var(--slate-900)',
            border: '1px solid var(--slate-200)',
            padding: '16px',
            borderRadius: '12px',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.12)',
            fontSize: '14px',
            fontWeight: '500',
          },
          success: {
            iconTheme: {
              primary: 'var(--success)',
              secondary: 'white',
            },
          },
          error: {
            iconTheme: {
              primary: 'var(--error)',
              secondary: 'white',
            },
          },
        }}
      />
      
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
                {user?.full_name || user?.username}
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
