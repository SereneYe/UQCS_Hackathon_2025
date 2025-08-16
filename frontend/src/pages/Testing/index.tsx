import React, { useState, useCallback, useEffect } from 'react';
import { User, Video } from '@/services';
import ApiDebugPanel from './components/ApiDebugPanel';
import UserApiTester from './components/UserApiTester';
import { useConsoleLogger, LogData } from './hooks/useConsoleLogger';

interface TestingPageState {
	users: User[];
	selectedUser: User | null;
	videos: Video[];
	selectedVideo: Video | null;
	testHistory: LogData[];
	debugResults: unknown[];
}

const TestingPage: React.FC = () => {
	const [pageState, setPageState] = useState<TestingPageState>({
		users: [],
		selectedUser: null,
		videos: [],
		selectedVideo: null,
		testHistory: [],
		debugResults: []
	});
	
	const [isDevMode, setIsDevMode] = useState(() => {
		return process.env.NODE_ENV === 'development' ||
			window.location.hostname === 'localhost' ||
			window.location.search.includes('debug=true');
	});
	
	const logger = useConsoleLogger();
	
	// Define callback functions - must be declared before the useEffect that uses them
	const clearAllResults = useCallback(() => {
		logger.clearLogs();
		setPageState(prev => ({
			...prev,
			testHistory: [],
			debugResults: []
		}));
		localStorage.removeItem('api-test-history');
	}, [logger]);
	
	const exportTestResults = useCallback(() => {
		const exportData = {
			timestamp: new Date().toISOString(),
			testHistory: pageState.testHistory,
			currentState: {
				usersCount: pageState.users.length,
				videosCount: pageState.videos.length,
				selectedUser: pageState.selectedUser,
				selectedVideo: pageState.selectedVideo
			},
			debugResults: pageState.debugResults
		};
		
		logger.exportLogs(pageState.testHistory);
		
		const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
		const filename = `complete-test-state-${timestamp}.json`;
		
		const dataStr = JSON.stringify(exportData, null, 2);
		const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
		
		const linkElement = document.createElement('a');
		linkElement.setAttribute('href', dataUri);
		linkElement.setAttribute('download', filename);
		linkElement.click();
	}, [pageState, logger]);
	
	const saveTestHistory = useCallback(() => {
		try {
			localStorage.setItem('api-test-history', JSON.stringify(pageState.testHistory));
			console.log('📁 Test history saved to localStorage');
		} catch (error) {
			console.error('Failed to save test history:', error);
		}
	}, [pageState.testHistory]);
	
	// Expose test results to global window object
	useEffect(() => {
		(window as Window & { apiTestResults?: TestingPageState }).apiTestResults = pageState;
	}, [pageState]);
	
	// Keyboard shortcut support
	useEffect(() => {
		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.ctrlKey || event.metaKey) {
				switch (event.key.toLowerCase()) {
					case 't':
						event.preventDefault();
						clearAllResults();
						break;
					case 'e':
						event.preventDefault();
						exportTestResults();
						break;
					case 's':
						event.preventDefault();
						saveTestHistory();
						break;
				}
			}
		};
		
		window.addEventListener('keydown', handleKeyDown);
		return () => window.removeEventListener('keydown', handleKeyDown);
	}, [clearAllResults, exportTestResults, saveTestHistory]);
	
	// Load test history from localStorage
	useEffect(() => {
		const savedHistory = localStorage.getItem('api-test-history');
		if (savedHistory) {
			try {
				const history = JSON.parse(savedHistory);
				setPageState(prev => ({...prev, testHistory: history}));
			} catch (error) {
				console.warn('Failed to load test history:', error);
			}
		}
	}, []);
	
	const handleUserDataUpdate = useCallback((data: { users: User[], selectedUser: User | null }) => {
		setPageState(prev => ({
			...prev,
			users: data.users,
			selectedUser: data.selectedUser
		}));
	}, []);
	
	const handleVideoDataUpdate = useCallback((data: { videos: Video[], selectedVideo: Video | null }) => {
		setPageState(prev => ({
			...prev,
			videos: data.videos,
			selectedVideo: data.selectedVideo
		}));
	}, []);
	
	const handleDebugResult = useCallback((result: unknown) => {
		setPageState(prev => ({
			...prev,
			debugResults: [result, ...prev.debugResults.slice(0, 9)] // Keep latest 10 results
		}));
	}, []);
	
	const runAllTests = useCallback(async () => {
		logger.logTestStart('Complete API Test Suite');
		logger.logTestSeparator();
		
		console.log('🚀 Starting complete API test suite...');
		console.log('📊 Current data status:', {
			users: pageState.users.length,
			videos: pageState.videos.length
		});
		
		// Here we can trigger all component tests
		// Since components are independent, we only log start and end
		logger.logTestSeparator();
		logger.logTestEnd('Complete API Test Suite');
	}, [logger, pageState]);
	
	// If not in development mode, show information message
	if (!isDevMode) {
		return (
			<div className="min-h-screen bg-gray-50 flex items-center justify-center">
				<div className="bg-white rounded-lg shadow-md p-8 max-w-md text-center">
					<div className="text-6xl mb-4">🔒</div>
					<h2 className="text-2xl font-bold text-gray-800 mb-2">Testing Page</h2>
					<p className="text-gray-600 mb-4">
						This page is only available in development environment.
					</p>
					<p className="text-sm text-gray-500">
						To access in production, add <code>?debug=true</code> parameter to the URL.
					</p>
					<button
						onClick={() => setIsDevMode(true)}
						className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
					>
						Force Enable
					</button>
				</div>
			</div>
		);
	}
	
	return (
		<div className="min-h-screen bg-gray-50">
			{/* Page Header */}
			<div className="bg-white shadow-sm border-b">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div className="py-6">
						<div className="flex items-center justify-between">
							<div>
								<h1 className="text-3xl font-bold text-gray-900">🧪 API Testing Center</h1>
								<p className="text-gray-600 mt-1">
									Test and debug user and video related API interfaces
								</p>
							</div>
							
							{/* Global Control Buttons */}
							<div className="flex items-center gap-3">
								<div className="text-sm text-gray-500">
									<div>Users: {pageState.users.length} items</div>
									<div>Videos: {pageState.videos.length} items</div>
								</div>
								
								<button
									onClick={runAllTests}
									className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
								>
									🚀 Run All Tests
								</button>
								
								<button
									onClick={exportTestResults}
									className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
									title="Ctrl/Cmd + E"
								>
									📊 Export Results
								</button>
								
								<button
									onClick={clearAllResults}
									className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
									title="Ctrl/Cmd + T"
								>
									🧹 Clear All
								</button>
							</div>
						</div>
						
						{/* Keyboard Shortcuts */}
						<div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
							<div className="text-sm text-blue-800">
								<strong>Shortcuts:</strong>
								<span className="ml-2">Ctrl/Cmd + T (Clear)</span>
								<span className="ml-4">Ctrl/Cmd + E (Export)</span>
								<span className="ml-4">Ctrl/Cmd + S (Save History)</span>
							</div>
						</div>
					</div>
				</div>
			</div>
			
			{/* Main Content Area */}
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<div className="space-y-8">
					{/* Overview Information Cards */}
					<div className="grid grid-cols-1 md:grid-cols-4 gap-6">
						<div className="bg-white rounded-lg shadow-md p-6">
							<div className="flex items-center">
								<div className="p-3 bg-blue-100 rounded-full">
									<span className="text-2xl">👥</span>
								</div>
								<div className="ml-4">
									<h3 className="text-lg font-semibold text-gray-800">User Data</h3>
									<p className="text-2xl font-bold text-blue-600">{pageState.users.length}</p>
									{pageState.selectedUser && (
										<p className="text-sm text-gray-500">Selected: {pageState.selectedUser.email}</p>
									)}
								</div>
							</div>
						</div>
						
						<div className="bg-white rounded-lg shadow-md p-6">
							<div className="flex items-center">
								<div className="p-3 bg-green-100 rounded-full">
									<span className="text-2xl">🎥</span>
								</div>
								<div className="ml-4">
									<h3 className="text-lg font-semibold text-gray-800">Video Data</h3>
									<p className="text-2xl font-bold text-green-600">{pageState.videos.length}</p>
									{pageState.selectedVideo && (
										<p className="text-sm text-gray-500">Selected:
											ID {pageState.selectedVideo.id}</p>
									)}
								</div>
							</div>
						</div>
						
						<div className="bg-white rounded-lg shadow-md p-6">
							<div className="flex items-center">
								<div className="p-3 bg-purple-100 rounded-full">
									<span className="text-2xl">🔧</span>
								</div>
								<div className="ml-4">
									<h3 className="text-lg font-semibold text-gray-800">Debug Results</h3>
									<p className="text-2xl font-bold text-purple-600">{pageState.debugResults.length}</p>
									<p className="text-sm text-gray-500">Recent debug records</p>
								</div>
							</div>
						</div>
						
						<div className="bg-white rounded-lg shadow-md p-6">
							<div className="flex items-center">
								<div className="p-3 bg-orange-100 rounded-full">
									<span className="text-2xl">📋</span>
								</div>
								<div className="ml-4">
									<h3 className="text-lg font-semibold text-gray-800">Test History</h3>
									<p className="text-2xl font-bold text-orange-600">{pageState.testHistory.length}</p>
									<p className="text-sm text-gray-500">Number of history records</p>
								</div>
							</div>
						</div>
					</div>
					
					{/* API Debug Panel */}
					<ApiDebugPanel onResult={handleDebugResult}/>
					
					{/* User API Tester */}
					<UserApiTester onDataUpdate={handleUserDataUpdate}/>
					
					{/* Recent Debug Results */}
					{pageState.debugResults.length > 0 && (
						<div className="bg-white rounded-lg shadow-md p-6">
							<h3 className="text-lg font-semibold text-gray-800 mb-4">🔍 Recent Debug Results</h3>
							<div className="space-y-3">
								{pageState.debugResults.slice(0, 3).map((result, index) => (
									<div key={index} className="bg-gray-50 border border-gray-200 rounded p-3">
										<div className="text-xs text-gray-500 mb-1">Result #{index + 1}</div>
										<pre className="text-sm text-gray-700 overflow-x-auto">
                      {JSON.stringify(result, null, 2)}
                    </pre>
									</div>
								))}
								{pageState.debugResults.length > 3 && (
									<div className="text-center">
                    <span className="text-sm text-gray-500">
                      {pageState.debugResults.length - 3} more results...
                    </span>
									</div>
								)}
							</div>
						</div>
					)}
				</div>
			</div>
			
			{/* Page Footer Information */}
			<div className="bg-white border-t mt-16">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
					<div className="text-center text-sm text-gray-500">
						<p>
							API Testing Page - Only available in development environment or debug mode
						</p>
						<p className="mt-1">
							All API calls and test results are logged in detail in the browser console
						</p>
						<p className="mt-1">
							Test results are exposed to <code>window.apiTestResults</code> for console access
						</p>
					</div>
				</div>
			</div>
		</div>
	);
};

export default TestingPage;