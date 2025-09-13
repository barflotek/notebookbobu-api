-- Client CRM Database Schema for Supabase
-- Add these tables to your Supabase database

-- Enable Row Level Security for all tables
-- These will be created in your existing Supabase project

-- Clients table (main entity)
CREATE TABLE IF NOT EXISTS notebookbobu_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Basic info
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    
    -- Business context
    client_type VARCHAR(50) DEFAULT 'prospect' CHECK (client_type IN ('prospect', 'beginner', 'intermediate', 'advanced', 'instructor')),
    status VARCHAR(50) DEFAULT 'prospect' CHECK (status IN ('active', 'inactive', 'prospect', 'archived')),
    
    -- Preferences
    preferred_contact VARCHAR(50) DEFAULT 'email' CHECK (preferred_contact IN ('email', 'phone', 'sms', 'whatsapp', 'in_person')),
    equipment_preference VARCHAR(50) DEFAULT 'none' CHECK (equipment_preference IN ('sabre', 'epee', 'foil', 'all', 'none')),
    
    -- Emergency contact
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(50),
    
    -- Business tracking
    referral_source VARCHAR(255),
    referred_clients TEXT[], -- Array of client IDs they referred
    
    -- Lesson context
    total_lessons INTEGER DEFAULT 0,
    last_lesson_date TIMESTAMP WITH TIME ZONE,
    
    -- Payment context
    outstanding_balance DECIMAL(10,2) DEFAULT 0.00,
    payment_preference VARCHAR(50),
    
    -- Analytics
    engagement_score DECIMAL(3,2) DEFAULT 0.00,
    document_count INTEGER DEFAULT 0,
    
    -- Timestamps
    join_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_contact_date TIMESTAMP WITH TIME ZONE,
    
    -- Flexible metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Communications table (unified timeline)
CREATE TABLE IF NOT EXISTS notebookbobu_communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES notebookbobu_clients(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Communication details
    type VARCHAR(50) NOT NULL CHECK (type IN ('email', 'phone_call', 'sms', 'whatsapp', 'in_person', 'document', 'note')),
    subject VARCHAR(500),
    content TEXT,
    
    -- Document linkage
    document_id UUID, -- References notebookbobu_documents.id (soft reference for now)
    
    -- Call/meeting specific
    duration_minutes INTEGER,
    outcome VARCHAR(255),
    
    -- Email/message specific
    direction VARCHAR(50) DEFAULT 'outbound' CHECK (direction IN ('inbound', 'outbound')),
    is_read BOOLEAN DEFAULT true,
    
    -- Follow-up tracking
    requires_followup BOOLEAN DEFAULT false,
    followup_date TIMESTAMP WITH TIME ZONE,
    followup_completed BOOLEAN DEFAULT false,
    
    -- AI analysis
    sentiment VARCHAR(50) CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    key_topics TEXT[],
    urgency_level VARCHAR(50) DEFAULT 'normal' CHECK (urgency_level IN ('urgent', 'high', 'normal', 'low')),
    
    -- Timestamps
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Flexible metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Tasks table (follow-ups and actions)
CREATE TABLE IF NOT EXISTS notebookbobu_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES notebookbobu_clients(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Task details
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type VARCHAR(100) DEFAULT 'follow_up',
    
    -- Scheduling
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Status and priority
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    priority VARCHAR(50) DEFAULT 'normal' CHECK (priority IN ('urgent', 'high', 'normal', 'low')),
    
    -- AI context
    is_ai_suggested BOOLEAN DEFAULT false,
    ai_reasoning TEXT,
    
    -- Communication linkage
    related_communication_id UUID REFERENCES notebookbobu_communications(id) ON DELETE SET NULL,
    related_document_id UUID, -- Soft reference to documents
    
    -- Results tracking
    outcome VARCHAR(500),
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Flexible metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Client insights table (AI-generated)
CREATE TABLE IF NOT EXISTS notebookbobu_client_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES notebookbobu_clients(id) ON DELETE CASCADE,
    
    -- Communication analysis
    communication_frequency VARCHAR(50),
    last_interaction_days INTEGER,
    preferred_topics TEXT[],
    
    -- Business insights
    risk_level VARCHAR(50) DEFAULT 'low' CHECK (risk_level IN ('high', 'medium', 'low')),
    engagement_trend VARCHAR(50) DEFAULT 'stable' CHECK (engagement_trend IN ('improving', 'declining', 'stable')),
    
    -- AI suggestions
    suggested_actions TEXT[],
    follow_up_priority VARCHAR(50) DEFAULT 'normal' CHECK (follow_up_priority IN ('urgent', 'high', 'normal', 'low')),
    
    -- Generated content
    summary TEXT,
    key_notes TEXT[],
    
    -- Timestamps
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(client_id) -- One insight record per client (upsert pattern)
);

-- Update existing documents table to include client relationship
ALTER TABLE notebookbobu_documents 
ADD COLUMN IF NOT EXISTS client_id UUID REFERENCES notebookbobu_clients(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS client_context VARCHAR(100);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_clients_user_id ON notebookbobu_clients(user_id);
CREATE INDEX IF NOT EXISTS idx_clients_status ON notebookbobu_clients(status);
CREATE INDEX IF NOT EXISTS idx_clients_type ON notebookbobu_clients(client_type);
CREATE INDEX IF NOT EXISTS idx_clients_last_contact ON notebookbobu_clients(last_contact_date);

CREATE INDEX IF NOT EXISTS idx_communications_client_id ON notebookbobu_communications(client_id);
CREATE INDEX IF NOT EXISTS idx_communications_user_id ON notebookbobu_communications(user_id);
CREATE INDEX IF NOT EXISTS idx_communications_type ON notebookbobu_communications(type);
CREATE INDEX IF NOT EXISTS idx_communications_occurred_at ON notebookbobu_communications(occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_communications_followup ON notebookbobu_communications(requires_followup) WHERE requires_followup = true;

CREATE INDEX IF NOT EXISTS idx_tasks_client_id ON notebookbobu_tasks(client_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON notebookbobu_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON notebookbobu_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON notebookbobu_tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON notebookbobu_tasks(priority);

CREATE INDEX IF NOT EXISTS idx_documents_client_id ON notebookbobu_documents(client_id);

-- Row Level Security (RLS) Policies
ALTER TABLE notebookbobu_clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE notebookbobu_communications ENABLE ROW LEVEL SECURITY;
ALTER TABLE notebookbobu_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE notebookbobu_client_insights ENABLE ROW LEVEL SECURITY;

-- Clients policies
CREATE POLICY "Users can manage their own clients" 
ON notebookbobu_clients FOR ALL 
USING (auth.uid() = user_id);

-- Communications policies
CREATE POLICY "Users can manage their client communications" 
ON notebookbobu_communications FOR ALL 
USING (auth.uid() = user_id);

-- Tasks policies  
CREATE POLICY "Users can manage their own tasks"
ON notebookbobu_tasks FOR ALL
USING (auth.uid() = user_id);

-- Client insights policies
CREATE POLICY "Users can view insights for their clients"
ON notebookbobu_client_insights FOR SELECT
USING (client_id IN (SELECT id FROM notebookbobu_clients WHERE user_id = auth.uid()));

CREATE POLICY "System can insert/update insights"
ON notebookbobu_client_insights FOR INSERT
WITH CHECK (true);

CREATE POLICY "System can update insights"
ON notebookbobu_client_insights FOR UPDATE
USING (true);

-- Update triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON notebookbobu_clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_communications_updated_at BEFORE UPDATE ON notebookbobu_communications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON notebookbobu_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();