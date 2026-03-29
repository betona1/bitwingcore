/** Bitwing 공통 타입 정의 */

// API 공통 응답
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data: T
}

// 페이지네이션 메타
export interface PaginationMeta {
  page: number
  size: number
  total: number
  total_pages: number
}

// 일정
export interface CalendarEvent {
  id: number
  title: string
  description?: string
  start_at: string
  end_at: string
  location?: string
  status: string
  google_event_id?: string
}

// 할일
export interface Todo {
  id: number
  title: string
  description?: string
  priority: 'urgent' | 'high' | 'normal' | 'low'
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  due_date?: string
  assigned_manager?: string
  created_at: string
}

// 메모
export interface Memo {
  id: number
  title?: string
  content: string
  category?: string
  tags?: string[]
  created_at: string
}

// 가계부
export interface FinanceTransaction {
  id: number
  type: 'income' | 'expense'
  amount: number
  category: string
  subcategory?: string
  description?: string
  payment_method?: string
  merchant?: string
  transaction_date: string
}

export interface FinanceSummary {
  period: string
  total_income: number
  total_expense: number
  balance: number
  expense_by_category: Record<string, number>
}

// 매니저
export interface Manager {
  code_name: string
  display_name: string
  role: string
  managed_modules: string[]
  status?: string
  total_tasks?: number
  last_active_at?: string
}

// PC
export interface ManagedPC {
  id: number
  hostname: string
  ip_address?: string
  os_type: string
  employee_name?: string
  department?: string
  status: 'online' | 'offline' | 'maintenance'
  last_seen_at?: string
}

// 이메일
export interface EmailItem {
  id: number
  subject?: string
  sender?: string
  received_at?: string
  is_read: boolean
  provider: string
}

// 채팅
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  intent?: string
  manager?: string
}
