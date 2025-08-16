import React, { useState, useCallback } from 'react';
import { apiClient } from '@/services';
import { useConsoleLogger } from '../hooks/useConsoleLogger';

interface ApiDebugPanelProps {
  onResult?: (result: unknown) => void;
}

const ApiDebugPanel: React.FC<ApiDebugPanelProps> = ({ onResult }) => {
  const [method, setMethod] = useState<'GET' | 'POST' | 'PUT' | 'DELETE'>('GET');
  const [endpoint, setEndpoint] = useState('/users/');
  const [requestBody, setRequestBody] = useState('');
  const [response, setResponse] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(true);
  
  const logger = useConsoleLogger();

  const presetRequests = [
    { name: 'Get User List', method: 'GET' as const, endpoint: '/users/?skip=0&limit=10', body: '' },
    { name: 'Get Single User', method: 'GET' as const, endpoint: '/users/1', body: '' },
    { name: 'Create User', method: 'POST' as const, endpoint: '/users/', body: '{\n  "email": "test@example.com"\n}' },
  ];

  const executeRequest = useCallback(async () => {
    if (!endpoint.trim()) {
      setError('Please enter API endpoint');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    const requestData = requestBody.trim() ? JSON.parse(requestBody) : undefined;
    const logData = logger.logApiRequest(method, endpoint, {}, requestData);

    try {
      let result;
      switch (method) {
        case 'GET':
          result = await apiClient.get(endpoint);
          break;
        case 'POST':
          result = await apiClient.post(endpoint, requestData);
          break;
        case 'PUT':
          result = await apiClient.put(endpoint, requestData);
          break;
        case 'DELETE':
          result = await apiClient.delete(endpoint);
          break;
        default:
          throw new Error('Unsupported HTTP method');
      }

      setResponse(result);
      logger.logApiSuccess(endpoint, result, logData.startTime);
      onResult?.(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      logger.logApiError(endpoint, err, logData.startTime);
    } finally {
      setLoading(false);
    }
  }, [method, endpoint, requestBody, logger, onResult]);

  const loadPreset = useCallback((preset: typeof presetRequests[0]) => {
    setMethod(preset.method);
    setEndpoint(preset.endpoint);
    setRequestBody(preset.body);
    setResponse(null);
    setError(null);
  }, []);

  const formatJson = useCallback((obj: unknown): string => {
    if (obj === null) return 'null';
    if (obj === undefined) return 'undefined';
    try {
      return JSON.stringify(obj, null, 2);
    } catch {
      return String(obj);
    }
  }, []);

  const parseRequestBody = useCallback(() => {
    if (!requestBody.trim()) return;
    try {
      const parsed = JSON.parse(requestBody);
      setRequestBody(JSON.stringify(parsed, null, 2));
      setError(null);
    } catch (err) {
      setError('JSON format error: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  }, [requestBody]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">🛠️ API Debug Panel</h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-gray-500 hover:text-gray-700 transition-colors"
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      {isExpanded && (
        <>
          {/* Preset Requests */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preset Requests
            </label>
            <div className="flex flex-wrap gap-2">
              {presetRequests.map((preset, index) => (
                <button
                  key={index}
                  onClick={() => loadPreset(preset)}
                  className="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200 transition-colors"
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {/* HTTP Method Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                HTTP Method
              </label>
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value as typeof method)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Endpoint
              </label>
              <input
                type="text"
                value={endpoint}
                onChange={(e) => setEndpoint(e.target.value)}
                placeholder="/users/"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Request Body */}
          {(method === 'POST' || method === 'PUT') && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">
                  Request Body (JSON)
                </label>
                <button
                  onClick={parseRequestBody}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  Format JSON
                </button>
              </div>
              <textarea
                value={requestBody}
                onChange={(e) => setRequestBody(e.target.value)}
                placeholder='{\n  "key": "value"\n}'
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              />
            </div>
          )}

          {/* Execute Button */}
          <div className="flex gap-2 mb-4">
            <button
              onClick={executeRequest}
              disabled={loading}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                loading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {loading ? 'Executing...' : '🚀 Execute Request'}
            </button>

            <button
              onClick={() => {
                setResponse(null);
                setError(null);
                setRequestBody('');
              }}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
            >
              🧹 Clear Results
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800 text-sm">
                <span className="font-medium">❌ Error:</span> {error}
              </p>
            </div>
          )}

          {/* Response Display */}
          {response !== null && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">📊 Response Results</h4>
              <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
                <pre className="text-sm text-gray-800 whitespace-pre-wrap overflow-x-auto">
                  {formatJson(response)}
                </pre>
              </div>
            </div>
          )}

          {/* Status Indicators */}
          <div className="flex items-center gap-4 text-sm">
            <div className={`flex items-center gap-1 ${
              loading ? 'text-blue-600' : 'text-gray-400'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                loading ? 'bg-blue-600 animate-pulse' : 'bg-gray-300'
              }`}></div>
              <span>Request Status: {loading ? 'Executing' : 'Ready'}</span>
            </div>
            
            {response !== null && (
              <div className="flex items-center gap-1 text-green-600">
                <div className="w-2 h-2 rounded-full bg-green-600"></div>
                <span>Last Request: Success</span>
              </div>
            )}
            
            {error && (
              <div className="flex items-center gap-1 text-red-600">
                <div className="w-2 h-2 rounded-full bg-red-600"></div>
                <span>Last Request: Failed</span>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ApiDebugPanel;