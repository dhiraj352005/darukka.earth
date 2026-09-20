import { useEffect, useRef, useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import mapboxgl from 'mapbox-gl'
import MapboxDraw from '@mapbox/mapbox-gl-draw'
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css'
import 'mapbox-gl/dist/mapbox-gl.css'
import { siteAPI, projectAPI } from '../services/api'
import './MapView.css'

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

const MapView = ({ onSiteClick, isAdmin }) => {
  const mapContainer = useRef(null)
  const map = useRef(null)
  const draw = useRef(null)
  const [sites, setSites] = useState([])
  const [drawnFeatures, setDrawnFeatures] = useState([])
  const [loading, setLoading] = useState(false)
  const [webglSupported, setWebglSupported] = useState(true)
  const [webglError, setWebglError] = useState(null)
  const [componentError, setComponentError] = useState(null)
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [saveFormData, setSaveFormData] = useState({
    siteName: '',
    description: '',
    projectId: '',
    createNewProject: false,
    projectName: ''
  })

  // Check WebGL support on mount
  useEffect(() => {
    const checkWebGL = () => {
      const canvas = document.createElement('canvas')
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
      
      if (!gl) {
        return { supported: false, error: 'WebGL is not supported by your browser or device' }
      }
      
      // Try to create a WebGL context to verify it works
      try {
        const extension = gl.getExtension('WEBGL_lose_context')
        if (extension) {
          extension.loseContext()
        }
        return { supported: true, error: null }
      } catch (e) {
        return { supported: false, error: 'WebGL context creation failed: ' + e.message }
      }
    }

    const result = checkWebGL()
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setWebglSupported(result.supported)
    if (result.error) {
      setWebglError(result.error)
    }
  }, [])

  const addSitesToMap = useCallback((sitesData) => {
    if (!map.current || !sitesData || !Array.isArray(sitesData) || sitesData.length === 0) return

    // Remove existing source and layer if they exist
    if (map.current.getLayer('sites-layer')) {
      map.current.removeLayer('sites-layer')
    }
    if (map.current.getLayer('sites-outline')) {
      map.current.removeLayer('sites-outline')
    }
    if (map.current.getSource('sites')) {
      map.current.removeSource('sites')
    }

    // Convert sites to GeoJSON
    const geojsonFeatures = sitesData.map((site) => {
      let geometry
      try {
        // Parse the geometry string from the API, or use it directly if already an object
        geometry = typeof site.geometry === 'string' ? JSON.parse(site.geometry) : site.geometry
      } catch (e) {
        console.error('Error parsing geometry for site:', site.id, e)
        return null
      }

      return {
        type: 'Feature',
        properties: {
          id: site.id,
          name: site.name,
          description: site.description,
          project_id: site.project_id,
          area_hectares: site.area_hectares,
        },
        geometry: geometry,
      }
    }).filter(Boolean)

    const geojson = {
      type: 'FeatureCollection',
      features: geojsonFeatures,
    }

    // Add source
    map.current.addSource('sites', {
      type: 'geojson',
      data: geojson,
    })

    // Add fill layer
    map.current.addLayer({
      id: 'sites-layer',
      type: 'fill',
      source: 'sites',
      paint: {
        'fill-color': '#088',
        'fill-opacity': 0.4,
      },
    })

    // Add outline layer
    map.current.addLayer({
      id: 'sites-outline',
      type: 'line',
      source: 'sites',
      paint: {
        'line-color': '#088',
        'line-width': 2,
      },
    })

    // Add click event to sites
    map.current.on('click', 'sites-layer', (e) => {
      if (e.features.length > 0) {
        const feature = e.features[0]
        if (onSiteClick) {
          onSiteClick(feature.properties)
        }
      }
    })

    // Change cursor on hover
    map.current.on('mouseenter', 'sites-layer', () => {
      map.current.getCanvas().style.cursor = 'pointer'
    })

    map.current.on('mouseleave', 'sites-layer', () => {
      map.current.getCanvas().style.cursor = ''
    })

    // Fit map to show all sites
    if (geojsonFeatures.length > 0) {
      const bounds = new mapboxgl.LngLatBounds()
      geojsonFeatures.forEach((feature) => {
        feature.geometry.coordinates[0].forEach((coord) => {
          bounds.extend(coord)
        })
      })
      map.current.fitBounds(bounds, { padding: 50 })
    }
  }, [onSiteClick])

  const loadSites = useCallback(async () => {
    try {
      const sitesData = await siteAPI.getAll()
      
      // Ensure sitesData is an array
      const sites = Array.isArray(sitesData) ? sitesData : []
      
      setSites(sites)

      // Wait for map to be ready
      if (!map.current.isStyleLoaded()) {
        map.current.on('load', () => addSitesToMap(sites))
      } else {
        addSitesToMap(sites)
      }
    } catch (error) {
      console.error('Error loading sites:', error)
      setSites([]) // Set empty array on error
    }
  }, [addSitesToMap])

  const updateDrawnFeatures = useCallback(() => {
    if (draw.current) {
      const data = draw.current.getAll()
      setDrawnFeatures(data.features)
    }
  }, [])

  // Initialize map
  useEffect(() => {
    if (map.current) return // Initialize map only once
    if (!webglSupported) return // Don't initialize if WebGL not supported

    try {
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/satellite-streets-v12',
        center: [77.5946, 12.9716], // Bangalore, India as default
        zoom: 12,
        failIfMajorPerformanceCaveat: false, // Don't fail on performance issues
        preserveDrawingBuffer: true, // Better compatibility
      })

      // Handle WebGL context loss
      map.current.on('error', (e) => {
        console.error('Mapbox error:', e.error)
        if (e.error && e.error.message && e.error.message.includes('WebGL')) {
          setWebglSupported(false)
          setWebglError('WebGL context lost. Please refresh the page or try a different browser.')
        }
      })

      // Add navigation controls
      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right')

      // Add fullscreen control
      map.current.addControl(new mapboxgl.FullscreenControl(), 'top-right')

      // Initialize Mapbox Draw for admins
      if (isAdmin) {
        draw.current = new MapboxDraw({
          displayControlsDefault: false,
          controls: {
            polygon: true,
            trash: true,
          },
          defaultMode: 'simple_select',
        })
        map.current.addControl(draw.current, 'top-left')

        // Listen to draw events
        map.current.on('draw.create', updateDrawnFeatures)
        map.current.on('draw.update', updateDrawnFeatures)
        map.current.on('draw.delete', updateDrawnFeatures)
      }

      // Load existing sites
      if (map.current) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        loadSites().catch(error => {
          console.error('Failed to load sites:', error)
        })
      }
    } catch (error) {
      console.error('Map initialization error:', error)
      setWebglSupported(false)
      setWebglError('Failed to initialize map: ' + error.message)
    }

    return () => {
      if (map.current) {
        map.current.remove()
        map.current = null
      }
    }
  }, [isAdmin, loadSites, updateDrawnFeatures, webglSupported])

  const handleSaveDrawings = async () => {
    if (!drawnFeatures || drawnFeatures.length === 0) {
      alert('No polygons drawn. Please draw at least one polygon on the map.')
      return
    }

    setShowSaveModal(true)
  }

  const handleSaveFormSubmit = async (e) => {
    e.preventDefault()
    
    if (!saveFormData.siteName) {
      alert('Please enter a site name')
      return
    }

    setLoading(true)
    let projectId
    
    try {
      if (saveFormData.createNewProject) {
        if (!saveFormData.projectName) {
          alert('Please enter a project name')
          setLoading(false)
          return
        }

        const projectData = {
          name: saveFormData.projectName,
          description: `Project containing ${saveFormData.siteName}`,
          status: 'active'
        }

        const projectResponse = await projectAPI.create(projectData)
        // API now returns data directly
        projectId = projectResponse.data?.id || projectResponse.id
      } else {
        projectId = parseInt(saveFormData.projectId)
        if (isNaN(projectId)) {
          alert('Please enter a valid project ID or create a new project')
          setLoading(false)
          return
        }
      }

      // Extract geometry from drawn feature
      const geometry = drawnFeatures[0].geometry

      // Create the site with proper authentication
      const siteData = {
        name: saveFormData.siteName,
        description: saveFormData.description || 'Site created from map interface',
        project_id: projectId,
        geometry: geometry,
        location_info: 'Created via map interface',
      }

      const response = await siteAPI.create(siteData)
      
      console.log('Site creation response:', response)
      
      // Show success message with analytics
      // API returns {data: {...}, analytics: {...}, message: "..."}
      const siteInfo = response.data || response
      const analytics = response.analytics || {}
      
      console.log('Site info:', siteInfo)
      console.log('Analytics:', analytics)
      
      alert(
        `✓ Site "${siteInfo.name}" created successfully!\n\n` +
        `📍 Area: ${siteInfo.area_hectares || analytics.area_hectares || 0} hectares\n` +
        `🌳 Estimated Trees: ${analytics.estimated_trees || 0}\n` +
        `♻️ CO2 Sequestration: ${analytics.co2_sequestration_annual || 0} tons/year`
      )

      // Store site info with analytics for immediate display
      const siteWithAnalytics = {
        ...siteInfo,
        analytics: analytics
      }
      console.log('Site created with analytics:', siteWithAnalytics)

      // Clear drawings
      if (draw.current) {
        draw.current.deleteAll()
        setDrawnFeatures([])
      }

      // Reset form
      setSaveFormData({
        siteName: '',
        description: '',
        projectId: '',
        createNewProject: false,
        projectName: ''
      })
      setShowSaveModal(false)

      // Reload sites
      await loadSites()
      
      // Trigger analytics modal - with safety checks
      if (onSiteClick && siteInfo && siteInfo.id) {
        setTimeout(() => {
          try {
            onSiteClick({
              id: siteInfo.id,
              name: siteInfo.name || 'Unknown Site',
              description: siteInfo.description || '',
              project_id: siteInfo.project_id || projectId,
              area_hectares: siteInfo.area_hectares || analytics.area_hectares || 0,
              analytics: analytics
            })
          } catch (modalError) {
            console.error('Error opening analytics modal:', modalError)
          }
        }, 500)
      }

    } catch (error) {
      console.error('Error saving site:', error)
      console.error('Error response:', error.response)
      console.error('Error data:', error.response?.data)
      
      let errorMsg = 'Failed to save site'
      
      if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMsg = error.response.data.message
      } else if (error.message) {
        errorMsg = error.message
      } else if (typeof error === 'string') {
        errorMsg = error
      }
      
      alert('Failed to save: ' + errorMsg)
      
    } finally {
      // Don't crash the app - ensure loading is reset
      setLoading(false)
    }
  }

  const handleClearDrawings = () => {
    if (draw.current) {
      draw.current.deleteAll()
      setDrawnFeatures([])
    }
  }

  return (
    <div className="map-view">
      {componentError ? (
        <div className="webgl-error">
          <div className="error-content">
            <h2>⚠️ An Error Occurred</h2>
            <p><strong>Error:</strong> {componentError}</p>
            <button 
              onClick={() => {
                setComponentError(null)
                window.location.reload()
              }} 
              className="btn btn-primary"
              style={{ marginTop: '20px' }}
            >
              🔄 Reload Page
            </button>
          </div>
        </div>
      ) : !webglSupported ? (
        <div className="webgl-error">
          <div className="error-content">
            <h2>⚠️ Map Display Not Available</h2>
            <p><strong>WebGL Error:</strong> {webglError}</p>
            <div className="error-details">
              <h3>Possible Solutions:</h3>
              <ul>
                <li>Try using a different browser (Chrome, Firefox, Edge)</li>
                <li>Enable hardware acceleration in your browser settings</li>
                <li>Update your graphics drivers</li>
                <li>Try refreshing the page</li>
              </ul>
              <h3>Browser Compatibility:</h3>
              <ul>
                <li>✓ Chrome 56+</li>
                <li>✓ Firefox 49+</li>
                <li>✓ Safari 10.1+</li>
                <li>✓ Edge 79+</li>
              </ul>
            </div>
            <button 
              onClick={() => window.location.reload()} 
              className="btn btn-primary"
              style={{ marginTop: '20px' }}
            >
              🔄 Refresh Page
            </button>
          </div>
        </div>
      ) : (
        <>
          <div ref={mapContainer} className="map-container" />
          
          {isAdmin && (
            <div className="map-controls">
              <div className="control-panel">
                <h3>Drawing Tools</h3>
                <p className="control-hint">
                  Use the polygon tool (top-left) to draw new sites
                </p>
                <div className="control-stats">
                  <span>Drawn polygons: {drawnFeatures.length}</span>
                </div>
                <div className="control-buttons">
                  <button
                    onClick={handleSaveDrawings}
                    disabled={drawnFeatures.length === 0 || loading}
                    className="btn btn-primary"
                  >
                    {loading ? 'Saving...' : '💾 Save Site'}
                  </button>
                  <button
                    onClick={handleClearDrawings}
                    disabled={drawnFeatures.length === 0}
                    className="btn btn-secondary"
                  >
                    🗑️ Clear
                  </button>
                  <button
                    onClick={loadSites}
                    className="btn btn-secondary"
                  >
                    🔄 Refresh Sites
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="map-info">
            <span>Total sites: {sites.length}</span>
          </div>
        </>
      )}

      {/* Save Site Modal */}
      {showSaveModal && (
        <div className="modal-overlay" onClick={() => setShowSaveModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>💾 Save Conservation Site</h2>
              <button className="close-btn" onClick={() => setShowSaveModal(false)}>✕</button>
            </div>
            
            <form onSubmit={handleSaveFormSubmit} className="save-form">
              <div className="form-group">
                <label htmlFor="siteName">Site Name *</label>
                <input
                  type="text"
                  id="siteName"
                  value={saveFormData.siteName}
                  onChange={(e) => setSaveFormData({...saveFormData, siteName: e.target.value})}
                  placeholder="Enter site name"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  value={saveFormData.description}
                  onChange={(e) => setSaveFormData({...saveFormData, description: e.target.value})}
                  placeholder="Enter site description (optional)"
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={saveFormData.createNewProject}
                    onChange={(e) => setSaveFormData({...saveFormData, createNewProject: e.target.checked})}
                  />
                  Create new project for this site
                </label>
              </div>

              {saveFormData.createNewProject ? (
                <div className="form-group">
                  <label htmlFor="projectName">New Project Name *</label>
                  <input
                    type="text"
                    id="projectName"
                    value={saveFormData.projectName}
                    onChange={(e) => setSaveFormData({...saveFormData, projectName: e.target.value})}
                    placeholder="Enter project name"
                    required={saveFormData.createNewProject}
                  />
                </div>
              ) : (
                <div className="form-group">
                  <label htmlFor="projectId">Project ID *</label>
                  <input
                    type="number"
                    id="projectId"
                    value={saveFormData.projectId}
                    onChange={(e) => setSaveFormData({...saveFormData, projectId: e.target.value})}
                    placeholder="Enter existing project ID"
                    required={!saveFormData.createNewProject}
                  />
                </div>
              )}

              <div className="form-actions">
                <button
                  type="button"
                  onClick={() => setShowSaveModal(false)}
                  className="btn btn-secondary"
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Saving...' : '💾 Save Site'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

MapView.propTypes = {
  onSiteClick: PropTypes.func,
  isAdmin: PropTypes.bool.isRequired,
}

export default MapView
