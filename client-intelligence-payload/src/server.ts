import express from 'express'
import payload from 'payload'

require('dotenv').config()

let app: express.Express

const initPayload = async (): Promise<express.Express> => {
  if (app) return app

  const expressApp = express()

  // Initialize Payload
  await payload.init({
    secret: process.env.PAYLOAD_SECRET!,
    express: expressApp,
    onInit: async () => {
      payload.logger.info(`Payload Admin URL: ${payload.getAdminURL()}`)
    },
  })

  // Redirect root to Admin panel
  expressApp.get('/', (_, res) => {
    res.redirect('/admin')
  })

  // Basic health check endpoint
  expressApp.get('/api/health', (req, res) => {
    res.json({
      status: 'healthy',
      service: 'Client Intelligence System',
      version: '1.0.0',
      timestamp: new Date().toISOString()
    })
  })

  app = expressApp
  return app
}

// For local development
if (process.env.NODE_ENV !== 'production') {
  const start = async () => {
    const localApp = await initPayload()
    const PORT = process.env.PORT || 3001
    
    localApp.listen(PORT, () => {
      payload.logger.info(`🚀 Client Intelligence System is running on port ${PORT}!`)
    })
  }
  
  start().catch(console.error)
}

// Export for Vercel
export default async (req: any, res: any) => {
  const app = await initPayload()
  return app(req, res)
}