import { useEffect, useRef, useState } from 'react'
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

  // Initialize map
  useEffect(() => {
    if (map.current) return // Initialize map only once

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: [77.5946, 12.9716], // Bangalore, India as default
      zoom: 12,
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
    loadSites()

    return () => {
      if (map.current) {
        map.current.remove()
        map.current = null
      }
    }
  }, [isAdmin])

  const updateDrawnFeatures = () => {
    if (draw.current) {
      const data = draw.current.getAll()
      setDrawnFeatures(data.features)
    }
  }

  const loadSites = async () => {
    try {
      const response = await siteAPI.getAll()
      const sitesData = response.data

      setSites(sitesData)

      // Wait for map to be ready
      if (!map.current.isStyleLoaded()) {
        map.current.on('load', () => addSitesToMap(sitesData))
      } else {
        addSitesToMap(sitesData)
      }
    } catch (error) {
      console.error('Error loading sites:', error)
    }
  }

  const addSitesToMap = (sitesData) => {
    if (!map.current || !sitesData || sitesData.length === 0) return

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
        // Parse the geometry string from the API
        geometry = JSON.parse(site.geometry)
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
  }

  const handleSaveDrawings = async () => {
    if (!drawnFeatures || drawnFeatures.length === 0) {
      alert('No polygons drawn. Please draw at least one polygon on the map.')
      return
    }

    const siteName = prompt('Enter a name for this site:')
    if (!siteName) return

    // Ask if user wants to create a new project or use existing
    const createNewProject = confirm(
      'Do you want to create a NEW project for this site?\n\n' +
      'Click OK to create a new project\n' +
      'Click Cancel to use an existing project'
    )

    setLoading(true)
    let projectId

    try {
      if (createNewProject) {
        // Create a new project
        const projectName = prompt('Enter project name:', `Project for ${siteName}`)
        if (!projectName) {
          setLoading(false)
          return
        }

        const projectData = {
          name: projectName,
          description: `Project containing ${siteName}`,
          status: 'active'
        }

        const projectResponse = await projectAPI.create(projectData)
        projectId = projectResponse.data.id
        alert(`✓ New project created with ID: ${projectId}`)
      } else {
        // Use existing project
        const projectIdInput = prompt('Enter existing project ID:', '1')
        if (!projectIdInput) {
          setLoading(false)
          return
        }
        
        projectId = parseInt(projectIdInput)
        if (isNaN(projectId)) {
          alert('Invalid project ID. Please enter a number.')
          setLoading(false)
          return
        }
      }

      // Create the site
      const siteData = {
        name: siteName,
        description: 'Site created from map',
        project_id: projectId,
        geometry: drawnFeatures[0].geometry, // Take first drawn polygon
        area_hectares: Math.floor(Math.random() * 100) + 10, // Placeholder calculation
        location_info: 'Created via map interface',
      }

      await siteAPI.create(siteData)
      alert('✓ Site saved successfully!')

      // Clear drawings
      if (draw.current) {
        draw.current.deleteAll()
        setDrawnFeatures([])
      }

      // Reload sites
      loadSites()
    } catch (error) {
      console.error('Error saving site:', error)
      const errorMsg = error.response?.data?.detail || error.message
      alert('Failed to save: ' + errorMsg)
    } finally {
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
    </div>
  )
}

export default MapView
