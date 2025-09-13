import express from 'express'
import payload from 'payload'

require('dotenv').config()
const app = express()

// Redirect root to Admin panel
app.get('/', (_, res) => {
  res.redirect('/admin')
})

const start = async () => {
  // Initialize Payload
  await payload.init({
    secret: process.env.PAYLOAD_SECRET!,
    express: app,
    onInit: async () => {
      payload.logger.info(`Payload Admin URL: ${payload.getAdminURL()}`)
    },
  })

  // Basic health check endpoint
  app.get('/api/health', (req, res) => {
    res.json({
      status: 'healthy',
      service: 'Client Intelligence System',
      version: '1.0.0',
      timestamp: new Date().toISOString()
    })
  })

  // Start server
  const PORT = process.env.PORT || 3001
  
  app.listen(PORT, async () => {
    payload.logger.info(`
🚀 Client Intelligence System is running!
    
Admin Panel: http://localhost:${PORT}/admin
GraphQL:     http://localhost:${PORT}/api/graphql
REST API:    http://localhost:${PORT}/api
    
Client Portal APIs:
- Dashboard:      GET /api/client-dashboard/:clientId
- Recommendations: GET /api/client-recommendations/:clientId  
- Progress:       GET /api/client-progress/:clientId
- Unified Portal: GET /api/unified-portal/:clientId
- MindBody Sync:  POST /api/sync-mindbody/:clientId
    `)
  })
}

start()