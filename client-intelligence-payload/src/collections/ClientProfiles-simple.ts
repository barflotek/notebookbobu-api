import { CollectionConfig } from 'payload/types'

export const ClientProfiles: CollectionConfig = {
  slug: 'client-profiles',
  admin: {
    useAsTitle: 'name',
    description: 'Client profiles for behavioral intelligence tracking',
  },
  access: {
    read: () => true,
    create: () => true,
    update: () => true,
    delete: () => true,
  },
  fields: [
    // Core Identity
    {
      name: 'name',
      type: 'text',
      required: true,
      index: true,
    },
    {
      name: 'email',
      type: 'email',
      unique: true,
      index: true,
    },
    {
      name: 'phone',
      type: 'text',
    },
    {
      name: 'dateOfBirth',
      type: 'date',
    },

    // Business Context
    {
      name: 'businessOwner',
      type: 'text',
      required: true,
      admin: {
        description: 'Business/coach who manages this client',
      },
    },
    {
      name: 'clientId',
      type: 'text',
      unique: true,
      admin: {
        description: 'Unique ID for external system integration',
      },
    },

    // Status
    {
      name: 'status',
      type: 'select',
      options: [
        { label: 'Active', value: 'active' },
        { label: 'Inactive', value: 'inactive' },
        { label: 'Prospective', value: 'prospective' },
        { label: 'Former', value: 'former' },
      ],
      defaultValue: 'active',
    },

    // Basic Preferences
    {
      name: 'preferences',
      type: 'group',
      fields: [
        {
          name: 'communicationChannel',
          type: 'select',
          options: [
            { label: 'Email', value: 'email' },
            { label: 'SMS', value: 'sms' },
            { label: 'Phone', value: 'phone' },
            { label: 'In-person', value: 'in_person' },
          ],
          hasMany: true,
        },
        {
          name: 'timezone',
          type: 'text',
          defaultValue: 'UTC',
        },
      ],
    },

    // Basic Intelligence Scores
    {
      name: 'intelligenceScores',
      type: 'group',
      fields: [
        {
          name: 'engagementScore',
          type: 'number',
          min: 0,
          max: 100,
          defaultValue: 50,
          admin: {
            description: 'Overall engagement level (0-100)',
          },
        },
        {
          name: 'lastUpdated',
          type: 'date',
          defaultValue: () => new Date(),
        },
      ],
    },

    // Timestamps
    {
      name: 'firstInteraction',
      type: 'date',
      admin: {
        position: 'sidebar',
      },
    },
    {
      name: 'lastInteraction',
      type: 'date',
      admin: {
        position: 'sidebar',
      },
    },
  ],
  timestamps: true,
}