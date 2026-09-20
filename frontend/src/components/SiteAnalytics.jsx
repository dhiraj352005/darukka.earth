import { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
import axios from 'axios'
import './SiteAnalytics.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const SiteAnalytics = ({ site, onClose }) => {
  const [activeTab, setActiveTab] = useState('overview')
  const [analyticsData, setAnalyticsData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch analytics data from backend
  useEffect(() => {
    const fetchAnalytics = async () => {
      // If analytics already provided in site prop, use it
      if (site.analytics) {
        setAnalyticsData(site.analytics)
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const response = await axios.get(`${API_BASE_URL}/api/sites/${site.id}/analytics`)
        setAnalyticsData(response.data)
      } catch (err) {
        console.error('Error fetching analytics:', err)
        setError('Failed to load analytics data')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [site.id, site.analytics])

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  const historical = analyticsData?.historical_data || {}

  // Chart configurations
  const treeGrowthOptions = {
    chart: { type: 'line', height: 300 },
    title: { text: 'Tree Growth Over Time', style: { fontSize: '16px', fontWeight: '600' } },
    xAxis: { categories: historical.months || [], title: { text: 'Month' } },
    yAxis: { title: { text: 'Number of Trees' } },
    series: [{ name: 'Trees Planted', data: historical.tree_count || [], color: '#10b981' }],
    credits: { enabled: false },
    legend: { enabled: false },
  }

  const biodiversityOptions = {
    chart: { type: 'area', height: 300 },
    title: { text: 'Biodiversity Index', style: { fontSize: '16px', fontWeight: '600' } },
    xAxis: { categories: historical.months || [] },
    yAxis: { title: { text: 'Species Count' } },
    series: [{
      name: 'Species Observed',
      data: historical.biodiversity || [],
      fillColor: { linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 }, stops: [[0, '#3b82f6'], [1, 'rgba(59, 130, 246, 0.1)']] },
      color: '#3b82f6',
    }],
    credits: { enabled: false },
    legend: { enabled: false },
  }

  const carbonOptions = {
    chart: { type: 'column', height: 300 },
    title: { text: 'Carbon Sequestration', style: { fontSize: '16px', fontWeight: '600' } },
    xAxis: { categories: historical.months || [] },
    yAxis: { title: { text: 'Tons of CO₂' } },
    series: [{ name: 'CO₂ Captured', data: historical.co2_sequestration || [], color: '#8b5cf6' }],
    credits: { enabled: false },
    legend: { enabled: false },
  }

  const soilHealthOptions = {
    chart: { type: 'spline', height: 300 },
    title: { text: 'Soil Health Quality Score', style: { fontSize: '16px', fontWeight: '600' } },
    xAxis: { categories: historical.months || [] },
    yAxis: { title: { text: 'Quality Score (%)' }, min: 0, max: 100 },
    series: [{ name: 'Soil Quality', data: historical.soil_health || [], color: '#f59e0b' }],
    credits: { enabled: false },
    legend: { enabled: false },
  }

  const canopyCoverOptions = {
    chart: { type: 'area', height: 300 },
    title: { text: 'Canopy Cover Progress', style: { fontSize: '16px', fontWeight: '600' } },
    xAxis: { categories: historical.months || [] },
    yAxis: { title: { text: 'Coverage (%)' }, min: 0, max: 100 },
    series: [{
      name: 'Canopy Cover',
      data: historical.canopy_cover || [],
      fillColor: { linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 }, stops: [[0, '#10b981'], [1, 'rgba(16, 185, 129, 0.1)']] },
      color: '#10b981',
    }],
    credits: { enabled: false },
    legend: { enabled: false },
  }

  return (
    <div className="analytics-overlay" onClick={onClose}>
      <div className="analytics-modal" onClick={(e) => e.stopPropagation()}>
        <div className="analytics-header">
          <div>
            <h2>{site.name}</h2>
            <p className="site-description">{site.description || 'No description available'}</p>
            <div className="site-meta">
              <span className="meta-item">📍 Project ID: {site.project_id}</span>
              {site.area_hectares && <span className="meta-item">📏 Area: {site.area_hectares} hectares</span>}
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="loader"></div>
            <p>Loading analytics data...</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <p>⚠️ {error}</p>
          </div>
        ) : (
          <>
            <div className="analytics-tabs">
              <button className={activeTab === 'overview' ? 'tab active' : 'tab'} onClick={() => setActiveTab('overview')}>
                Overview
              </button>
              <button className={activeTab === 'detailed' ? 'tab active' : 'tab'} onClick={() => setActiveTab('detailed')}>
                Detailed Metrics
              </button>
            </div>

            <div className="analytics-content">
              {activeTab === 'overview' && (
                <div className="overview-grid">
                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: '#dcfce7' }}>🌳</div>
                    <div className="stat-content">
                      <h3>Estimated Trees</h3>
                      <p className="stat-value">{analyticsData.estimated_trees?.toLocaleString() || 0}</p>
                      <p className="stat-info">Based on {analyticsData.area_hectares} hectares</p>
                    </div>
                  </div>

                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: '#ede9fe' }}>♻️</div>
                    <div className="stat-content">
                      <h3>CO₂ Sequestration</h3>
                      <p className="stat-value">{analyticsData.co2_sequestration_annual} tons/year</p>
                      <p className="stat-info">Offsets {analyticsData.co2_offset_vehicles} vehicles annually</p>
                    </div>
                  </div>

                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: '#dbeafe' }}>🦋</div>
                    <div className="stat-content">
                      <h3>Biodiversity Score</h3>
                      <p className="stat-value">{analyticsData.biodiversity_score}</p>
                      <p className="stat-info">Species diversity index</p>
                    </div>
                  </div>

                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: '#fef3c7' }}>🌾</div>
                    <div className="stat-content">
                      <h3>Soil Health</h3>
                      <p className="stat-value">{analyticsData.soil_health_index}%</p>
                      <p className="stat-info">Quality index</p>
                    </div>
                  </div>

                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: '#fef2f2' }}>🌱</div>
                    <div className="stat-content">
                      <h3>Biomass</h3>
                      <p className="stat-value">{analyticsData.estimated_biomass_tons} tons</p>
                      <p className="stat-info">Total estimated biomass</p>
                    </div>
                  </div>

                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: '#dbeafe' }}>💧</div>
                    <div className="stat-content">
                      <h3>Canopy Cover</h3>
                      <p className="stat-value">{analyticsData.canopy_cover_percentage}%</p>
                      <p className="stat-info">Current coverage</p>
                    </div>
                  </div>

                  <div className="chart-container full-width">
                    <HighchartsReact highcharts={Highcharts} options={treeGrowthOptions} />
                  </div>

                  <div className="chart-container full-width">
                    <HighchartsReact highcharts={Highcharts} options={carbonOptions} />
                  </div>
                </div>
              )}

              {activeTab === 'detailed' && (
                <div className="detailed-grid">
                  <div className="chart-container">
                    <HighchartsReact highcharts={Highcharts} options={canopyCoverOptions} />
                  </div>
                  <div className="chart-container">
                    <HighchartsReact highcharts={Highcharts} options={soilHealthOptions} />
                  </div>
                  <div className="chart-container">
                    <HighchartsReact highcharts={Highcharts} options={treeGrowthOptions} />
                  </div>
                  <div className="chart-container">
                    <HighchartsReact highcharts={Highcharts} options={biodiversityOptions} />
                  </div>
                </div>
              )}
            </div>

            <div className="analytics-footer">
              <p className="disclaimer">
                📊 Analytics calculated using FAO and IPCC research-based estimates for reforestation projects.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

SiteAnalytics.propTypes = {
  site: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    project_id: PropTypes.number.isRequired,
    area_hectares: PropTypes.number,
    analytics: PropTypes.object,
  }).isRequired,
  onClose: PropTypes.func.isRequired,
}

export default SiteAnalytics
