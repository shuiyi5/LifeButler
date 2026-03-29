import { useState, useEffect } from 'react'
import { dashboardAPI } from '../services/api'

export const useDashboard = () => {
  const [overview, setOverview] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardAPI.getOverview().then(res => {
      setOverview(res.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  return { overview, loading }
}
