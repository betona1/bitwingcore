/** Zustand 전역 상태 관리 */

import { create } from 'zustand'
import type { ChatMessage, Manager, FinanceSummary } from '../types'

interface AppState {
  // 사이드바
  sidebarCollapsed: boolean
  toggleSidebar: () => void

  // 채팅
  chatMessages: ChatMessage[]
  addChatMessage: (msg: ChatMessage) => void
  clearChat: () => void

  // 매니저
  managers: Manager[]
  setManagers: (list: Manager[]) => void

  // 가계부 요약
  financeSummary: FinanceSummary | null
  setFinanceSummary: (s: FinanceSummary) => void
}

export const useAppStore = create<AppState>((set) => ({
  sidebarCollapsed: false,
  toggleSidebar: () =>
    set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),

  chatMessages: [],
  addChatMessage: (msg) =>
    set((s) => ({ chatMessages: [...s.chatMessages, msg] })),
  clearChat: () => set({ chatMessages: [] }),

  managers: [],
  setManagers: (list) => set({ managers: list }),

  financeSummary: null,
  setFinanceSummary: (s) => set({ financeSummary: s }),
}))
