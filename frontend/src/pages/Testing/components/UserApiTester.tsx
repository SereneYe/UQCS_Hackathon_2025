import React, { useState, useCallback, useEffect } from 'react';
import {
	useGetUsers,
	useGetUser,
	useGetUserByEmail,
	useCreateUser,
	User,
	UserCreate
} from '@/services';
import { useConsoleLogger } from '../hooks/useConsoleLogger';

interface UserApiTesterProps {
	onDataUpdate?: (data: { users: User[], selectedUser: User | null }) => void;
}

const UserApiTester: React.FC<UserApiTesterProps> = ({onDataUpdate}) => {
	const [skip, setSkip] = useState(0);
	const [limit, setLimit] = useState(10);
	const [userId, setUserId] = useState<number>(1);
	const [userEmail, setUserEmail] = useState('');
	const [newUserEmail, setNewUserEmail] = useState('test@example.com');
	const [isExpanded, setIsExpanded] = useState(true);
	const [testResults, setTestResults] = useState<Record<string, unknown>>({});
	
	const logger = useConsoleLogger();
	
	// API Hooks - disabled automatic fetching, only using refetch functions
	const {
		data: users,
		isLoading: usersLoading,
		error: usersError,
		refetch: refetchUsers
	} = useGetUsers(skip, limit, {enabled: false});
	
	const {
		data: user,
		isLoading: userLoading,
		error: userError,
		refetch: refetchUser
	} = useGetUser(userId, {enabled: false});
	
	const {
		data: userByEmail,
		isLoading: userByEmailLoading,
		error: userByEmailError,
		refetch: refetchUserByEmail
	} = useGetUserByEmail(userEmail, {enabled: false});
	
	const createUserMutation = useCreateUser();
	
	// Manual logging functions for API results (only called when user triggers actions)
	const logUserResults = useCallback((data: unknown, endpoint: string, startTime: number) => {
		if (data) {
			const count = Array.isArray(data) ? data.length : undefined;
			logger.logApiSuccess(endpoint, data, startTime, count);
			setTestResults(prev => ({...prev, [endpoint]: data}));
		}
	}, [logger]);
	
	const logUserError = useCallback((error: Error, endpoint: string, startTime: number) => {
		logger.logApiError(endpoint, error, startTime);
		setTestResults(prev => ({...prev, [`${endpoint}_error`]: error.message}));
	}, [logger]);
	
	// Update parent component with data
	useEffect(() => {
		onDataUpdate?.({
			users: users || [],
			selectedUser: user || null
		});
	}, [users, user, onDataUpdate]);
	
	// Test functions
	const testGetUsers = useCallback(async () => {
		logger.logTestStart('Get User List');
		const logData = logger.logApiRequest('GET', '/users/', {skip, limit});
		try {
			const result = await refetchUsers();
			if (result.data) {
				logger.logApiSuccess('/users/', result.data, logData.startTime, result.data.length);
			}
		} catch (error) {
			logger.logApiError('/users/', error, logData.startTime);
		}
		logger.logTestEnd('Get User List');
	}, [skip, limit, refetchUsers, logger]);
	
	const testGetUser = useCallback(async () => {
		logger.logTestStart('Get Single User');
		const logData = logger.logApiRequest('GET', `/users/${userId}`, {userId});
		try {
			const result = await refetchUser();
			if (result.data) {
				logger.logApiSuccess(`/users/${userId}`, result.data, logData.startTime);
			}
		} catch (error) {
			logger.logApiError(`/users/${userId}`, error, logData.startTime);
		}
		logger.logTestEnd('Get Single User');
	}, [userId, refetchUser, logger]);
	
	const testGetUserByEmail = useCallback(async () => {
		if (!userEmail.trim()) return;
		logger.logTestStart('Get User by Email');
		const logData = logger.logApiRequest('GET', `/users/email/${userEmail}`, {email: userEmail});
		try {
			const result = await refetchUserByEmail();
			if (result.data) {
				logger.logApiSuccess(`/users/email/${userEmail}`, result.data, logData.startTime);
			}
		} catch (error) {
			logger.logApiError(`/users/email/${userEmail}`, error, logData.startTime);
		}
		logger.logTestEnd('Get User by Email');
	}, [userEmail, refetchUserByEmail, logger]);
	
	const testCreateUser = useCallback(async () => {
		if (!newUserEmail.trim()) return;
		logger.logTestStart('Create New User');
		const userData: UserCreate = {email: newUserEmail};
		const logData = logger.logApiRequest('POST', '/users/', {}, userData);
		
		try {
			const result = await createUserMutation.mutateAsync(userData);
			logger.logApiSuccess('/users/', result, logData.startTime);
			setTestResults(prev => ({...prev, createdUser: result}));
			// Clear form and refresh user list
			setNewUserEmail('');
			refetchUsers();
		} catch (error) {
			logger.logApiError('/users/', error, logData.startTime);
			setTestResults(prev => ({
				...prev,
				createUserError: error instanceof Error ? error.message : 'Failed to create user'
			}));
		}
		logger.logTestEnd('Create New User');
	}, [newUserEmail, createUserMutation, logger, refetchUsers]);
	
	const testAllUserApis = useCallback(async () => {
		logger.logTestStart('Complete User API Test');
		logger.logTestSeparator();
		
		await testGetUsers();
		await new Promise(resolve => setTimeout(resolve, 500));
		
		await testGetUser();
		await new Promise(resolve => setTimeout(resolve, 500));
		
		if (userEmail.trim()) {
			await testGetUserByEmail();
			await new Promise(resolve => setTimeout(resolve, 500));
		}
		
		if (newUserEmail.trim()) {
			await testCreateUser();
		}
		
		logger.logTestSeparator();
		logger.logTestEnd('Complete User API Test');
	}, [testGetUsers, testGetUser, testGetUserByEmail, testCreateUser, userEmail, newUserEmail, logger]);
	
	const getStatusColor = (isLoading: boolean, error: unknown) => {
		if (isLoading) return 'text-blue-600';
		if (error) return 'text-red-600';
		return 'text-green-600';
	};
	
	const getStatusIcon = (isLoading: boolean, error: unknown) => {
		if (isLoading) return '🔄';
		if (error) return '❌';
		return '✅';
	};
	
	const formatJson = (obj: unknown): string => {
		if (obj === null || obj === undefined) return 'null';
		try {
			return JSON.stringify(obj, null, 2);
		} catch {
			return String(obj);
		}
	};
	
	return (
		<div className="bg-white rounded-lg shadow-md p-6 mb-6">
			<div className="flex items-center justify-between mb-4">
				<h3 className="text-lg font-semibold text-gray-800">👥 User API Tester</h3>
				<div className="flex items-center gap-2">
					<button
						onClick={testAllUserApis}
						className="px-3 py-1 text-sm bg-green-600 text-gray-900 rounded-md hover:bg-green-700 transition-colors"
					>
						🚀 Run All Tests
					</button>
					<button
						onClick={() => setIsExpanded(!isExpanded)}
						className="text-gray-500 hover:text-gray-700 transition-colors"
					>
						{isExpanded ? 'Collapse' : 'Expand'}
					</button>
				</div>
			</div>
			
			{isExpanded && (
				<>
					{/* API Status Overview */}
					<div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
						<div
							className={`p-3 rounded-md border ${usersError ? 'bg-red-50 border-red-200' : usersLoading ? 'bg-blue-50 border-blue-200' : 'bg-green-50 border-green-200'}`}>
							<div className={`text-sm font-medium ${getStatusColor(usersLoading, usersError)}`}>
								{getStatusIcon(usersLoading, usersError)} User List
							</div>
							<div className="text-xs text-gray-600 mt-1">
								{usersLoading ? 'Loading...' : usersError ? 'Failed' : `${users?.length || 0} items`}
							</div>
						</div>
						
						<div
							className={`p-3 rounded-md border ${userError ? 'bg-red-50 border-red-200' : userLoading ? 'bg-blue-50 border-blue-200' : 'bg-green-50 border-green-200'}`}>
							<div className={`text-sm font-medium ${getStatusColor(userLoading, userError)}`}>
								{getStatusIcon(userLoading, userError)} Single User
							</div>
							<div className="text-xs text-gray-600 mt-1">
								{userLoading ? 'Loading...' : userError ? 'Failed' : user ? 'Loaded' : 'No Data'}
							</div>
						</div>
						
						<div
							className={`p-3 rounded-md border ${userByEmailError ? 'bg-red-50 border-red-200' : userByEmailLoading ? 'bg-blue-50 border-blue-200' : 'bg-green-50 border-green-200'}`}>
							<div
								className={`text-sm font-medium ${getStatusColor(userByEmailLoading, userByEmailError)}`}>
								{getStatusIcon(userByEmailLoading, userByEmailError)} Email Query
							</div>
							<div className="text-xs text-gray-600 mt-1">
								{userByEmailLoading ? 'Loading...' : userByEmailError ? 'Failed' : userByEmail ? 'Found' : 'No Data'}
							</div>
						</div>
						
						<div
							className={`p-3 rounded-md border ${createUserMutation.isError ? 'bg-red-50 border-red-200' : createUserMutation.isPending ? 'bg-blue-50 border-blue-200' : 'bg-green-50 border-green-200'}`}>
							<div
								className={`text-sm font-medium ${getStatusColor(createUserMutation.isPending, createUserMutation.error)}`}>
								{getStatusIcon(createUserMutation.isPending, createUserMutation.error)} Create User
							</div>
							<div className="text-xs text-gray-600 mt-1">
								{createUserMutation.isPending ? 'Creating...' : createUserMutation.isError ? 'Failed' : 'Ready'}
							</div>
						</div>
					</div>
					
					{/* Test Controls */}
					<div className="space-y-4">
						{/* Get User List */}
						<div className="border border-gray-200 rounded-md p-4">
							<div className="flex items-center justify-between mb-3">
								<h4 className="font-medium text-gray-800">📋 Get User List (useGetUsers)</h4>
								<button
									onClick={testGetUsers}
									className="px-3 py-1 text-sm bg-blue-600 text-gray-900 rounded-md hover:bg-blue-700 transition-colors"
								>
									Test
								</button>
							</div>
							<div className="grid grid-cols-2 gap-3 mb-3">
								<div>
									<label className="block text-xs font-medium text-gray-700 mb-1">Skip</label>
									<input
										type="number"
										value={skip}
										onChange={(e) => setSkip(Number(e.target.value))}
										className="w-full px-2 py-1 border border-gray-300 rounded text-sm text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
									/>
								</div>
								<div>
									<label className="block text-xs font-medium text-gray-700 mb-1">Limit</label>
									<input
										type="number"
										value={limit}
										onChange={(e) => setLimit(Number(e.target.value))}
										className="w-full px-2 py-1 border border-gray-300 rounded text-sm text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
									/>
								</div>
							</div>
							{users && (
								<div className="bg-gray-50 border border-gray-200 rounded p-2">
									<div className="text-xs font-medium text-gray-700 mb-1">Results
										({users.length} items):
									</div>
									<pre className="text-xs text-gray-600 max-h-20 overflow-y-auto">
                    {formatJson(users)}
                  </pre>
								</div>
							)}
						</div>
						
						{/* Get Single User */}
						<div className="border border-gray-200 rounded-md p-4">
							<div className="flex items-center justify-between mb-3">
								<h4 className="font-medium text-gray-800">👤 Get Single User (useGetUser)</h4>
								<button
									onClick={testGetUser}
									className="px-3 py-1 text-sm bg-blue-600 text-gray-900 rounded-md hover:bg-blue-700 transition-colors"
								>
									Test
								</button>
							</div>
							<div className="mb-3">
								<label className="block text-xs font-medium text-gray-700 mb-1">User ID</label>
								<input
									type="number"
									value={userId}
									onChange={(e) => setUserId(Number(e.target.value))}
									className="w-full px-2 py-1 border border-gray-300 rounded text-sm text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
								/>
							</div>
							{user && (
								<div className="bg-gray-50 border border-gray-200 rounded p-2">
									<div className="text-xs font-medium text-gray-700 mb-1">Result:</div>
									<pre className="text-xs text-gray-600">
                    {formatJson(user)}
                  </pre>
								</div>
							)}
						</div>
						
						{/* Get User by Email */}
						<div className="border border-gray-200 rounded-md p-4">
							<div className="flex items-center justify-between mb-3">
								<h4 className="font-medium text-gray-800">📧 Get User by Email (useGetUserByEmail)</h4>
								<button
									onClick={testGetUserByEmail}
									className="px-3 py-1 text-sm bg-blue-600 text-gray-900 rounded-md hover:bg-blue-700 transition-colors"
									disabled={!userEmail.trim()}
								>
									Test
								</button>
							</div>
							<div className="mb-3">
								<label className="block text-xs font-medium text-gray-700 mb-1">User Email</label>
								<input
									type="email"
									value={userEmail}
									onChange={(e) => setUserEmail(e.target.value)}
									placeholder="test@example.com"
									className="w-full px-2 py-1 border border-gray-300 rounded text-sm text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
								/>
							</div>
							{userByEmail && (
								<div className="bg-gray-50 border border-gray-200 rounded p-2">
									<div className="text-xs font-medium text-gray-700 mb-1">Result:</div>
									<pre className="text-xs text-gray-600">
                    {formatJson(userByEmail)}
                  </pre>
								</div>
							)}
						</div>
						
						{/* Create User */}
						<div className="border border-gray-200 rounded-md p-4">
							<div className="flex items-center justify-between mb-3">
								<h4 className="font-medium text-gray-800">➕ Create User (useCreateUser)</h4>
								<button
									onClick={testCreateUser}
									className="px-3 py-1 text-sm bg-green-600 text-gray-900 rounded-md hover:bg-green-700 transition-colors"
									disabled={!newUserEmail.trim() || createUserMutation.isPending}
								>
									{createUserMutation.isPending ? 'Creating...' : 'Create'}
								</button>
							</div>
							<div className="mb-3">
								<label className="block text-xs font-medium text-gray-700 mb-1">New User Email</label>
								<input
									type="email"
									value={newUserEmail}
									onChange={(e) => setNewUserEmail(e.target.value)}
									placeholder="new@example.com"
									className="w-full px-2 py-1 border border-gray-300 rounded text-sm text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
								/>
							</div>
							{createUserMutation.data && (
								<div className="bg-green-50 border border-green-200 rounded p-2">
									<div className="text-xs font-medium text-green-700 mb-1">Creation Successful:</div>
									<pre className="text-xs text-green-600">
                    {formatJson(createUserMutation.data)}
                  </pre>
								</div>
							)}
							{createUserMutation.error && (
								<div className="bg-red-50 border border-red-200 rounded p-2">
									<div className="text-xs font-medium text-red-700 mb-1">Creation Failed:</div>
									<div className="text-xs text-red-600">
										{createUserMutation.error instanceof Error ? createUserMutation.error.message : 'Unknown error'}
									</div>
								</div>
							)}
						</div>
					</div>
				</>
			)}
		</div>
	);
};

export default UserApiTester;