// API клиент для взаимодействия с backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  agent_type: 'hr' | 'user';
  conversation_id?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface ChatResponse {
  response: string;
  agent_type: 'hr' | 'user';
  conversation_id?: string;
  processing_time: number;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: any;
}

export interface AudioTranscriptionResponse {
  text: string;
  agent_type: 'hr' | 'user';
  conversation_id?: string;
  processing_time: number;
  chat_response?: ChatResponse;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData: ErrorResponse = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async sendHRMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat/hr', {
      method: 'POST',
      body: JSON.stringify({
        message,
        agent_type: 'hr',
        conversation_id: conversationId,
      }),
    });
  }

  async sendUserMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat/user', {
      method: 'POST',
      body: JSON.stringify({
        message,
        agent_type: 'user',
        conversation_id: conversationId,
      }),
    });
  }

  async getHealth() {
    return this.request('/health');
  }

  async getAgents() {
    return this.request('/agents');
  }

  async transcribeAudio(
    audioFile: File, 
    agentType: 'hr' | 'user', 
    conversationId?: string
  ): Promise<AudioTranscriptionResponse> {
    const formData = new FormData();
    formData.append('file', audioFile);
    formData.append('agent_type', agentType);
    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }

    const url = `${this.baseUrl}/audio/transcriptions`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData: ErrorResponse = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }
}

export const apiClient = new ApiClient();
