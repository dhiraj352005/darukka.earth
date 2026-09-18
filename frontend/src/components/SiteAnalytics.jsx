import { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
import './SiteAnalytics.css'

const SiteAnalytics = ({ site, onClose }) => {
  const [activeTab, setActiveTab] = useState('overview')

  // Generate dummy data for demonstration
  const generateDummyData = () => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const currentMonth = new Date().getMonth()
    
    return {
      treeGrowth: months.slice(0, currentMonth + 1).map((month, index) => ({
        month,
        count: Math.floor(Math.random() * 500) + 1000 + (index * 100),
      })),
      biodiversity: months.slice(0, currentMonth + 1).map((month, index) => ({
        month,
        species: Math.floor(Math.random() * 20) + 50 + (index * 2),
      })),
      carbonSequestration: months.slice(0, currentMonth + 1).map((month, index) => ({
        month,
        tons: (Math.random() * 10 + 20 + (index * 1.5)).toFixed(2),
      })),
      soilHealth: months.slice(0, currentMonth + 1).map((month, index) => ({
        month,
        quality: (Math.random() * 10 + 70 + (index * 0.5)).toFixed(1),
      })),
    }
  }

  const [analyticsData] = useState(generateDummyData())

  // Tree Growth Chart Configuration
  const treeGrowthOptions = {
    chart: {
      type: 'line',
      height: 300,
    },
    title: {
      text: 'Tree Growth Over Time',
      style: {
        fontSize: '16px',
        fontWeight: '600',
      },
    },
    xAxis: {
      categories: analyticsData.treeGrowth.map((d) => d.month),
      title: {
        text: 'Month',
      },
    },
    yAxis: {
      title: {
        text: 'Number of Trees',
      },
    },
    series: [
      {
        name: 'Trees Planted',
        data: analyticsData.treeGrowth.map((d) => d.count),
        color: '#10b981',
      },
    ],
    credits: {
      enabled: false,
    },
    legend: {
      enabled: false,
    },
  }

  // Biodiversity Chart Configuration
  const biodiversityOptions = {
    chart: {
      type: 'area',
      height: 300,
    },
    title: {
      text: 'Biodiversity Index',
      style: {
        fontSize: '16px',
        fontWeight: '600',
      },
    },
    xAxis: {
      categories: analyticsData.biodiversity.map((d) => d.month),
    },
    yAxis: {
      title: {
        text: 'Species Count',
      },
    },
    series: [
      {
        name: 'Species Observed',
        data: analyticsData.biodiversity.map((d) => d.species),
        fillColor: {
          linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
          stops: [
            [0, '#3b82f6'],
            [1, 'rgba(59, 130, 246, 0.1)'],
          ],
        },
        color: '#3b82f6',
      },
    ],
    credits: {
      enabled: false,
    },
    legend: {
      enabled: false,
    },
  }

  // Carbon Sequestration Chart Configuration
  const carbonOptions = {
    chart: {
      type: 'column',
      height: 300,
    },
    title: {
      text: 'Carbon Sequestration',
      style: {
        fontSize: '16px',
        fontWeight: '600',
      },
    },
    xAxis: {
      categories: analyticsData.carbonSequestration.map((d) => d.month),
    },
    yAxis: {
      title: {
        text: 'Tons of CO₂',
      },
    },
    series: [
      {
        name: 'CO₂ Captured',
        data: analyticsData.carbonSequestration.map((d) => parseFloat(d.tons)),
        color: '#8b5cf6',
      },
    ],
    credits: {
      enabled: false,
    },
    legend: {
      enabled: false,
    },
  }

  // Soil Health Chart Configuration
  const soilHealthOptions = {
    chart: {
      type: 'spline',
      height: 300,
    },
    title: {
      text: 'Soil Health Quality Score',
      style: {
        fontSize: '16px',
        fontWeight: '600',
      },
    },
    xAxis: {
      categories: analyticsData.soilHealth.map((d) => d.month),
    },
    yAxis: {
      title: {
        text: 'Quality Score (%)',
      },
      min: 0,
      max: 100,
    },
    series: [
      {
        name: 'Soil Quality',
        data: analyticsData.soilHealth.map((d) => parseFloat(d.quality)),
        color: '#f59e0b',
      },
    ],
    credits: {
      enabled: false,
    },
    legend: {
      enabled: false,
    },
  }

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  return (
    <div className="analytics-overlay" onClick={onClose}>
      <div className="analytics-modal" onClick={(e) => e.stopPropagation()}>
        <div className="analytics-header">
          <div>
            <h2>{site.name}</h2>
            <p className="site-description">{site.description || 'No description available'}</p>
            <div className="site-meta">
              <span className="meta-item">
                📍 Project ID: {site.project_id}
              </span>
              {site.area_hectares && (
                <span className="meta-item">
                  📏 Area: {site.area_hectares} hectares
                </span>
              )}
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="analytics-tabs">
          <button
            className={activeTab === 'overview' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className={activeTab === 'detailed' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('detailed')}
          >
            Detailed Metrics
          </button>
        </div>

        <div className="analytics-content">
          {activeTab === 'overview' && (
            <div className="overview-grid">
              <div className="stat-card">
                <div className="stat-icon" style={{ background: '#dcfce7' }}>
                  🌳
                </div>
                <div className="stat-content">
                  <h3>Total Trees</h3>
                  <p className="stat-value">
                    {analyticsData.treeGrowth[analyticsData.treeGrowth.length - 1].count}
                  </p>
                  <p className="stat-change positive">+12% this month</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon" style={{ background: '#dbeafe' }}>
                  🦋
                </div>
                <div className="stat-content">
                  <h3>Species Count</h3>
                  <p className="stat-value">
                    {analyticsData.biodiversity[analyticsData.biodiversity.length - 1].species}
                  </p>
                  <p className="stat-change positive">+8% this month</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon" style={{ background: '#ede9fe' }}>
                  🌱
                </div>
                <div className="stat-content">
                  <h3>Carbon Captured</h3>
                  <p className="stat-value">
                    {analyticsData.carbonSequestration[
                      analyticsData.carbonSequestration.length - 1
                    ].tons}{' '}
                    tons
                  </p>
                  <p className="stat-change positive">+15% this month</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon" style={{ background: '#fef3c7' }}>
                  🌾
                </div>
                <div className="stat-content">
                  <h3>Soil Quality</h3>
                  <p className="stat-value">
                    {analyticsData.soilHealth[analyticsData.soilHealth.length - 1].quality}%
                  </p>
                  <p className="stat-change positive">+3% this month</p>
                </div>
              </div>

              <div className="chart-container full-width">
                <HighchartsReact highcharts={Highcharts} options={treeGrowthOptions} />
              </div>

              <div className="chart-container full-width">
                <HighchartsReact highcharts={Highcharts} options={biodiversityOptions} />
              </div>
            </div>
          )}

          {activeTab === 'detailed' && (
            <div className="detailed-grid">
              <div className="chart-container">
                <HighchartsReact highcharts={Highcharts} options={carbonOptions} />
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
            📊 Analytics data is for demonstration purposes. Real-time data integration coming soon.
          </p>
        </div>
      </div>
    </div>
  )
}

SiteAnalytics.propTypes = {
  site: PropTypes.shape({
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    project_id: PropTypes.number.isRequired,
    area_hectares: PropTypes.number,
  }).isRequired,
  onClose: PropTypes.func.isRequired,
}

export default SiteAnalytics
