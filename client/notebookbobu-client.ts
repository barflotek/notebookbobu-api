/**
 * NotebookBobu API Client for Inbox-Zero Integration
 * 
 * This client provides a TypeScript interface for interacting with the NotebookBobu API
 * from the inbox-zero application.
 */

export interface DocumentResponse {
  id: string;
  user_id: string;
  title: string;
  type: 'pdf' | 'txt' | 'md' | 'docx';
  status: 'uploaded' | 'processing' | 'completed' | 'failed';
  file_path?: string;
  file_size?: number;
  created_at: string;
  updated_at?: string;
  
  // Processing results
  summary?: string;
  bullet_points?: string;
  q_and_a?: string;
  mindmap_html?: string;
  topics?: string[];
  confidence?: string;
  cost_optimized?: boolean;
}

export interface DocumentProcessResponse {
  id: string;
  status: string;
  message: string;
  document: DocumentResponse;
}

export interface QueryResponse {
  success: boolean;
  answer?: string;
  sources?: string[];
  document_count?: number;
  error?: string;
}

export interface ChatHistoryResponse {
  id: string;
  query: string;
  answer: string;
  timestamp: string;
  document_ids?: string[];
}

export interface ApiError {
  detail: string;
}

export class NotebookBobuClient {
  private baseUrl: string;
  private apiKey: string;
  
  constructor(baseUrl?: string, apiKey?: string) {
    this.baseUrl = baseUrl || 'https://notebookbobu-g1wdc943m-sentinel-io.vercel.app';
    this.apiKey = apiKey || process.env.INBOX_ZERO_API_KEY || '';
    
    if (!this.apiKey) {
      throw new Error('API key is required. Set INBOX_ZERO_API_KEY environment variable or pass it to constructor.');
    }
  }
  
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}/api${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({ 
        detail: `HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(error.detail);
    }
    
    return response.json();
  }
  
  private async uploadFile(
    endpoint: string,
    file: File | Buffer,
    filename: string,
    title: string
  ): Promise<DocumentProcessResponse> {
    const formData = new FormData();
    
    if (file instanceof Buffer) {
      formData.append('file', new Blob([file]), filename);
    } else {
      formData.append('file', file);
    }
    formData.append('title', title);
    
    const response = await fetch(`${this.baseUrl}/api${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({ 
        detail: `HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(error.detail);
    }
    
    return response.json();
  }
  
  // Document Management
  
  /**
   * Process a document and extract insights
   */
  async processDocument(
    file: File | Buffer, 
    filename: string, 
    title: string
  ): Promise<DocumentProcessResponse> {
    return this.uploadFile('/process', file, filename, title);
  }
  
  /**
   * Process a document using the v2 API (enhanced processing)
   */
  async processDocumentV2(
    file: File | Buffer, 
    filename: string, 
    title: string
  ): Promise<DocumentProcessResponse> {
    return this.uploadFile('/v2/process', file, filename, title);
  }
  
  /**
   * Get all documents for the user
   */
  async getDocuments(): Promise<DocumentResponse[]> {
    return this.request<DocumentResponse[]>('/documents');
  }
  
  /**
   * Get all documents using the v2 API
   */
  async getDocumentsV2(): Promise<DocumentResponse[]> {
    return this.request<DocumentResponse[]>('/v2/documents');
  }
  
  /**
   * Get a specific document by ID
   */
  async getDocument(documentId: string): Promise<DocumentResponse> {
    return this.request<DocumentResponse>(`/documents/${documentId}`);
  }
  
  /**
   * Get a specific document by ID using v2 API
   */
  async getDocumentV2(documentId: string): Promise<DocumentResponse> {
    return this.request<DocumentResponse>(`/v2/documents/${documentId}`);
  }
  
  /**
   * Delete a document
   */
  async deleteDocument(documentId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  }
  
  /**
   * Delete a document using v2 API
   */
  async deleteDocumentV2(documentId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/v2/documents/${documentId}`, {
      method: 'DELETE',
    });
  }
  
  // Chat & Query
  
  /**
   * Query documents using natural language
   */
  async query(question: string, documentIds?: string[]): Promise<QueryResponse> {
    return this.request<QueryResponse>('/query', {
      method: 'POST',
      body: JSON.stringify({
        question: question,
        document_ids: documentIds,
      }),
    });
  }
  
  /**
   * Get chat history
   */
  async getChatHistory(): Promise<ChatHistoryResponse[]> {
    return this.request<ChatHistoryResponse[]>('/chat-history');
  }
  
  // Search & Discovery
  
  /**
   * Search documents by content
   */
  async searchDocuments(
    query: string, 
    limit: number = 10
  ): Promise<DocumentResponse[]> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });
    
    return this.request<DocumentResponse[]>(`/v2/search?${params}`);
  }
  
  /**
   * Get document chunks for detailed analysis
   */
  async getDocumentChunks(documentId: string): Promise<any[]> {
    return this.request<any[]>(`/v2/documents/${documentId}/chunks`);
  }
  
  // Health & Status
  
  /**
   * Check API health
   */
  async healthCheck(): Promise<any> {
    return this.request<any>('/health');
  }
  
  /**
   * Ping the API
   */
  async ping(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/ping');
  }
}

// Convenience functions for common use cases

/**
 * Create a NotebookBobu client with inbox-zero configuration
 */
export function createInboxZeroClient(apiKey?: string): NotebookBobuClient {
  return new NotebookBobuClient(
    'https://notebookbobu-g1wdc943m-sentinel-io.vercel.app',
    apiKey || 'inbox-zero-api-key-2024'
  );
}

/**
 * Process an email attachment with NotebookBobu
 */
export async function processEmailAttachment(
  client: NotebookBobuClient,
  file: File | Buffer,
  filename: string,
  emailSubject: string
): Promise<DocumentProcessResponse> {
  try {
    // Use v2 API for better processing
    const result = await client.processDocumentV2(
      file,
      filename,
      `Email: ${emailSubject}`
    );
    
    return result;
  } catch (error) {
    console.error('Failed to process email attachment:', error);
    throw error;
  }
}

/**
 * Get insights from processed documents
 */
export async function getDocumentInsights(
  client: NotebookBobuClient,
  documentId: string
): Promise<{
  summary: string;
  keyPoints: string[];
  topics: string[];
  confidence: string;
}> {
  try {
    const doc = await client.getDocumentV2(documentId);
    
    return {
      summary: doc.summary || 'No summary available',
      keyPoints: doc.bullet_points ? doc.bullet_points.split('\n').filter(Boolean) : [],
      topics: doc.topics || [],
      confidence: doc.confidence || 'unknown',
    };
  } catch (error) {
    console.error('Failed to get document insights:', error);
    throw error;
  }
}

/**
 * Ask questions about documents
 */
export async function askQuestion(
  client: NotebookBobuClient,
  question: string,
  documentIds?: string[]
): Promise<string> {
  try {
    const response = await client.query(question, documentIds);
    return response.answer;
  } catch (error) {
    console.error('Failed to ask question:', error);
    throw error;
  }
}

export default NotebookBobuClient;