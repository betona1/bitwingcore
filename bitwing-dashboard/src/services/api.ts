/** Bitwing API 클라이언트 */

import axios from 'axios'
import type { ApiResponse } from '../types'

const API_KEY = 'your-bitwing-api-key'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    Authorization: `Bearer ${API_KEY}`,
    'Content-Type': 'application/json',
  },
})

// 채팅
export const postChat = (message: string) =>
  api.post<ApiResponse>('/chat', { message })

// 매니저
export const getManagers = () =>
  api.get<ApiResponse>('/managers')

export const getManagerDetail = (name: string) =>
  api.get<ApiResponse>(`/managers/${name}`)

export const getManagerTasks = (name: string, page = 1) =>
  api.get<ApiResponse>(`/managers/${name}/tasks`, { params: { page } })

// 일정
export const getCalendars = (dateRange = '이번주', page = 1) =>
  api.get<ApiResponse>('/calendars', { params: { date_range: dateRange, page } })

export const createCalendar = (data: Record<string, unknown>) =>
  api.post<ApiResponse>('/calendars', data)

export const deleteCalendar = (id: number) =>
  api.delete<ApiResponse>(`/calendars/${id}`)

// 할일
export const getTodos = (params?: Record<string, unknown>) =>
  api.get<ApiResponse>('/todos', { params })

export const createTodo = (data: Record<string, unknown>) =>
  api.post<ApiResponse>('/todos', data)

export const completeTodo = (id: number) =>
  api.post<ApiResponse>(`/todos/${id}/complete`)

export const deleteTodo = (id: number) =>
  api.delete<ApiResponse>(`/todos/${id}`)

// 메모
export const getMemos = (params?: Record<string, unknown>) =>
  api.get<ApiResponse>('/memos', { params })

export const searchMemos = (q: string) =>
  api.get<ApiResponse>('/memos/search', { params: { q } })

export const createMemo = (data: Record<string, unknown>) =>
  api.post<ApiResponse>('/memos', data)

export const deleteMemo = (id: number) =>
  api.delete<ApiResponse>(`/memos/${id}`)

// 가계부
export const getTransactions = (params?: Record<string, unknown>) =>
  api.get<ApiResponse>('/finance/transactions', { params })

export const getFinanceSummary = (dateRange = '이번달') =>
  api.get<ApiResponse>('/finance/summary', { params: { date_range: dateRange } })

export const createTransaction = (data: Record<string, unknown>) =>
  api.post<ApiResponse>('/finance/transactions', data)

// 이메일
export const getEmails = (params?: Record<string, unknown>) =>
  api.get<ApiResponse>('/emails', { params })

// 파일
export const getFiles = (params?: Record<string, unknown>) =>
  api.get<ApiResponse>('/files', { params })

// PC
export const getPCs = (params?: Record<string, unknown>) =>
  api.get<ApiResponse>('/pcs', { params })

// 리포트
export const getDailyReport = () =>
  api.get<ApiResponse>('/reports/daily')

export const getWeeklyReport = () =>
  api.get<ApiResponse>('/reports/weekly')

export const getMonthlyReport = () =>
  api.get<ApiResponse>('/reports/monthly')

// 연동
export const getIntegrations = () =>
  api.get<ApiResponse>('/integrations')

export default api
