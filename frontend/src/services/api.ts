import { ENV } from '@/config/environment';

export class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

class ApiClient {
    async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const url = `${ENV.API_BASE_URL}${endpoint}`;
        const config: RequestInit = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new ApiError(response.status, `API Error: ${response.status} - ${errorText}`);
        }
        
        return response.json() as Promise<T>;
    }
    
    get<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, {method: 'GET'});
    }
    
    post<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        });
    }
    
    put<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined,
        });
    }
    
    delete<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, {method: 'DELETE'});
    }
}

export const apiClient = new ApiClient();