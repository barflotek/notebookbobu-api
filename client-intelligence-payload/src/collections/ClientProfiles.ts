import { CollectionConfig } from 'payload/types'

export const ClientProfiles: CollectionConfig = {
  slug: 'client-profiles',
  admin: {
    useAsTitle: 'fullName',
    defaultColumns: ['fullName', 'email', 'membershipStatus', 'riskLevel', 'lastActivity'],
    group: 'Client Intelligence',
  },
  access: {
    read: () => true, // Internal staff only in production
    create: () => true,
    update: () => true,
    delete: () => true,
  },
  fields: [
    // Core Identity
    {
      name: 'fullName',
      type: 'text',
      required: true,
      admin: {
        description: 'Client full name for identification',
      },
    },
    {
      name: 'email',
      type: 'email',
      required: true,
      unique: true,
    },
    {
      name: 'phone',
      type: 'text',
    },
    {
      name: 'clientId',
      type: 'text',
      required: true,
      unique: true,
      admin: {
        description: 'Unique ID for external system integration (MindBody, etc.)',
      },
    },

    // External System Integration
    {
      name: 'externalSystems',
      type: 'group',
      fields: [
        {
          name: 'mindbodyId',
          type: 'text',
          admin: {
            description: 'MindBody client ID for API integration',
          },
        },
        {
          name: 'stripeCustomerId',
          type: 'text',
        },
        {
          name: 'hubspotContactId',
          type: 'text',
        },
        {
          name: 'lastSync',
          type: 'date',
          admin: {
            description: 'Last successful sync with external systems',
          },
        },
      ],
    },

    // Business Context
    {
      name: 'membershipStatus',
      type: 'select',
      options: [
        { label: 'Prospect', value: 'prospect' },
        { label: 'Trial Member', value: 'trial' },
        { label: 'Active Member', value: 'active' },
        { label: 'Paused', value: 'paused' },
        { label: 'Cancelled', value: 'cancelled' },
        { label: 'Former Member', value: 'former' },
      ],
      defaultValue: 'prospect',
      required: true,
    },
    {
      name: 'membershipTier',
      type: 'select',
      options: [
        { label: 'Basic', value: 'basic' },
        { label: 'Premium', value: 'premium' },
        { label: 'Elite', value: 'elite' },
        { label: 'Unlimited', value: 'unlimited' },
      ],
    },
    {
      name: 'joinDate',
      type: 'date',
    },
    {
      name: 'lastActivity',
      type: 'date',
      admin: {
        description: 'Last recorded activity (class, email, portal login, etc.)',
      },
    },

    // Preferences & Behavior
    {
      name: 'preferences',
      type: 'group',
      fields: [
        {
          name: 'communicationMethod',
          type: 'select',
          options: [
            { label: 'Email', value: 'email' },
            { label: 'SMS', value: 'sms' },
            { label: 'Phone', value: 'phone' },
            { label: 'In-Person', value: 'in_person' },
            { label: 'App Notifications', value: 'app' },
          ],
          hasMany: true,
        },
        {
          name: 'preferredTimes',
          type: 'array',
          fields: [
            {
              name: 'dayOfWeek',
              type: 'select',
              options: [
                { label: 'Monday', value: 'monday' },
                { label: 'Tuesday', value: 'tuesday' },
                { label: 'Wednesday', value: 'wednesday' },
                { label: 'Thursday', value: 'thursday' },
                { label: 'Friday', value: 'friday' },
                { label: 'Saturday', value: 'saturday' },
                { label: 'Sunday', value: 'sunday' },
              ],
            },
            {
              name: 'timeSlot',
              type: 'select',
              options: [
                { label: 'Early Morning (5-8 AM)', value: 'early_morning' },
                { label: 'Morning (8-11 AM)', value: 'morning' },
                { label: 'Lunch (11 AM-2 PM)', value: 'lunch' },
                { label: 'Afternoon (2-5 PM)', value: 'afternoon' },
                { label: 'Evening (5-8 PM)', value: 'evening' },
                { label: 'Late Evening (8-11 PM)', value: 'late_evening' },
              ],
            },
          ],
        },
        {
          name: 'interests',
          type: 'array',
          fields: [
            {
              name: 'category',
              type: 'text',
            },
            {
              name: 'proficiencyLevel',
              type: 'select',
              options: [
                { label: 'Beginner', value: 'beginner' },
                { label: 'Intermediate', value: 'intermediate' },
                { label: 'Advanced', value: 'advanced' },
                { label: 'Expert', value: 'expert' },
              ],
            },
          ],
        },
      ],
    },

    // AI Intelligence Scores
    {
      name: 'intelligenceScores',
      type: 'group',
      admin: {
        description: 'AI-calculated intelligence about this client',
      },
      fields: [
        {
          name: 'engagementScore',
          type: 'number',
          min: 0,
          max: 100,
          admin: {
            description: 'Overall engagement level (0-100)',
          },
        },
        {
          name: 'satisfactionScore',
          type: 'number',
          min: 0,
          max: 100,
          admin: {
            description: 'Predicted satisfaction based on communications',
          },
        },
        {
          name: 'churnRisk',
          type: 'select',
          options: [
            { label: 'Low', value: 'low' },
            { label: 'Medium', value: 'medium' },
            { label: 'High', value: 'high' },
            { label: 'Critical', value: 'critical' },
          ],
          defaultValue: 'low',
        },
        {
          name: 'lifetimeValue',
          type: 'number',
          admin: {
            description: 'Predicted lifetime value in dollars',
          },
        },
        {
          name: 'growthPotential',
          type: 'select',
          options: [
            { label: 'High Potential', value: 'high' },
            { label: 'Moderate Potential', value: 'moderate' },
            { label: 'Low Potential', value: 'low' },
            { label: 'Stable', value: 'stable' },
          ],
        },
      ],
    },

    // Communication Patterns
    {
      name: 'communicationPatterns',
      type: 'group',
      fields: [
        {
          name: 'responseTime',
          type: 'select',
          options: [
            { label: 'Immediate (< 1 hour)', value: 'immediate' },
            { label: 'Fast (1-4 hours)', value: 'fast' },
            { label: 'Moderate (4-24 hours)', value: 'moderate' },
            { label: 'Slow (1-3 days)', value: 'slow' },
            { label: 'Very Slow (> 3 days)', value: 'very_slow' },
          ],
        },
        {
          name: 'communicationFrequency',
          type: 'select',
          options: [
            { label: 'Daily', value: 'daily' },
            { label: 'Few times per week', value: 'frequent' },
            { label: 'Weekly', value: 'weekly' },
            { label: 'Bi-weekly', value: 'biweekly' },
            { label: 'Monthly', value: 'monthly' },
            { label: 'Rarely', value: 'rarely' },
          ],
        },
        {
          name: 'preferredTopics',
          type: 'array',
          fields: [
            {
              name: 'topic',
              type: 'text',
            },
            {
              name: 'frequency',
              type: 'number',
              admin: {
                description: 'How often they ask about this topic',
              },
            },
          ],
        },
      ],
    },

    // Goals & Objectives
    {
      name: 'goals',
      type: 'array',
      fields: [
        {
          name: 'goal',
          type: 'text',
          required: true,
        },
        {
          name: 'category',
          type: 'select',
          options: [
            { label: 'Fitness', value: 'fitness' },
            { label: 'Skill Development', value: 'skill' },
            { label: 'Competition', value: 'competition' },
            { label: 'Social', value: 'social' },
            { label: 'Health', value: 'health' },
            { label: 'Personal Growth', value: 'personal' },
          ],
        },
        {
          name: 'priority',
          type: 'select',
          options: [
            { label: 'High', value: 'high' },
            { label: 'Medium', value: 'medium' },
            { label: 'Low', value: 'low' },
          ],
        },
        {
          name: 'targetDate',
          type: 'date',
        },
        {
          name: 'progress',
          type: 'number',
          min: 0,
          max: 100,
          admin: {
            description: 'Progress percentage (0-100)',
          },
        },
      ],
    },

    // Relationships to other collections
    {
      name: 'interactions',
      type: 'relationship',
      relationTo: 'interactions',
      hasMany: true,
      admin: {
        description: 'All interactions with this client',
      },
    },
    {
      name: 'recommendations',
      type: 'relationship',
      relationTo: 'recommendations',
      hasMany: true,
      admin: {
        description: 'Active recommendations for this client',
      },
    },
    {
      name: 'behavioralInsights',
      type: 'relationship',
      relationTo: 'behavioral-insights',
      hasMany: true,
    },

    // Metadata
    {
      name: 'tags',
      type: 'array',
      fields: [
        {
          name: 'tag',
          type: 'text',
        },
      ],
      admin: {
        description: 'Custom tags for segmentation and filtering',
      },
    },
    {
      name: 'notes',
      type: 'richText',
      admin: {
        description: 'Staff notes about this client',
      },
    },
  ],
  hooks: {
    afterChange: [
      async ({ doc, operation }) => {
        // Trigger AI analysis after client profile changes
        if (operation === 'update') {
          // Queue background job to update behavioral insights
          // await queueBehavioralAnalysis(doc.id);
        }
      },
    ],
  },
  timestamps: true,
}