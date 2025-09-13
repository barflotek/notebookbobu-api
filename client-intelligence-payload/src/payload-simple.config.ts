import { buildConfig } from 'payload/config'
import path from 'path'
import { mongooseAdapter } from '@payloadcms/db-mongodb'
import { webpackBundler } from '@payloadcms/bundler-webpack'
import { slateEditor } from '@payloadcms/richtext-slate'

// Simple Collections
import { Users } from './collections/Users'
import { ClientProfiles } from './collections/ClientProfiles-simple'

export default buildConfig({
  admin: {
    user: Users.slug,
    bundler: webpackBundler(),
  },
  editor: slateEditor({}),
  collections: [
    Users,
    ClientProfiles,
  ],
  typescript: {
    outputFile: path.resolve(__dirname, '../payload-types.ts'),
  },
  graphQL: {
    schemaOutputFile: path.resolve(__dirname, '../generated-schema.graphql'),
  },
  db: mongooseAdapter({
    url: process.env.DATABASE_URI || '',
  }),
  cors: [
    'http://localhost:3000',
    'https://your-client-portal.com',
    'https://notebookbobu.vercel.app',
  ],
  csrf: [
    'http://localhost:3000',
    'https://your-client-portal.com', 
    'https://notebookbobu.vercel.app',
  ],
})