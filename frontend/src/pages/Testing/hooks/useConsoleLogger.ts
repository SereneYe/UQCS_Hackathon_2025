import { useCallback } from 'react';

export interface LogData {
	timestamp: string;
	method: string;
	endpoint: string;
	params?: Record<string, unknown>;
	data?: unknown;
	response?: unknown;
	error?: string;
	duration?: number;
	status: 'loading' | 'success' | 'error';
}

export const useConsoleLogger = () => {
	const logApiRequest = useCallback((method: string, endpoint: string, params?: Record<string, unknown>, data?: unknown) => {
		const timestamp = new Date().toLocaleTimeString();
		console.log(`🚀 [${timestamp}] API Request: ${method} ${endpoint}`);
		if (params && Object.keys(params).length > 0) {
			console.log('📋 Request Params:', params);
		}
		if (data) {
			console.log('📄 Request Data:', data);
		}
		return {timestamp, startTime: Date.now()};
	}, []);
	
	const logApiSuccess = useCallback((endpoint: string, response: unknown, startTime: number, count?: number) => {
		const timestamp = new Date().toLocaleTimeString();
		const duration = Date.now() - startTime;
		
		if (Array.isArray(response)) {
			console.log(`✅ [${timestamp}] API Success: Retrieved ${response.length} records`);
		} else if (count !== undefined) {
			console.log(`✅ [${timestamp}] API Success: Retrieved ${count} records`);
		} else {
			console.log(`✅ [${timestamp}] API Success: ${endpoint}`);
		}
		
		console.log('📊 Response Data:', response);
		console.log(`⏱️ Request Duration: ${duration}ms`);
		
		return {timestamp, duration, response};
	}, []);
	
	const logApiError = useCallback((endpoint: string, error: unknown, startTime: number) => {
		const timestamp = new Date().toLocaleTimeString();
		const duration = Date.now() - startTime;
		
		console.error(`❌ [${timestamp}] API Error: ${endpoint}`);
		console.error('💥 Error Info:', error);
		console.log(`⏱️ Request Duration: ${duration}ms`);
		
		return {timestamp, duration, error};
	}, []);
	
	const logTestStart = useCallback((testName: string) => {
		console.group(`🧪 Starting Test: ${testName}`);
		console.log(`⏰ Test Start Time: ${new Date().toLocaleTimeString()}`);
	}, []);
	
	const logTestEnd = useCallback((testName: string) => {
		console.log(`✅ Test Complete: ${testName}`);
		console.log(`⏰ Test End Time: ${new Date().toLocaleTimeString()}`);
		console.groupEnd();
	}, []);
	
	const logTestSeparator = useCallback(() => {
		console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
	}, []);
	
	const clearLogs = useCallback(() => {
		console.clear();
		console.log('🧹 Test logs cleared');
	}, []);
	
	const exportLogs = useCallback((logs: LogData[]) => {
		const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
		const filename = `api-test-results-${timestamp}.json`;
		
		const dataStr = JSON.stringify(logs, null, 2);
		const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
		
		const exportFileDefaultName = filename;
		const linkElement = document.createElement('a');
		linkElement.setAttribute('href', dataUri);
		linkElement.setAttribute('download', exportFileDefaultName);
		linkElement.click();
		
		console.log(`💾 Test results exported: ${filename}`);
	}, []);
	
	return {
		logApiRequest,
		logApiSuccess,
		logApiError,
		logTestStart,
		logTestEnd,
		logTestSeparator,
		clearLogs,
		exportLogs,
	};
};