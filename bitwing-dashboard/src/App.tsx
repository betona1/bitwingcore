import { Routes, Route } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import DashboardPage from './pages/DashboardPage'
import ChatPage from './pages/ChatPage'
import ManagersPage from './pages/ManagersPage'
import CalendarPage from './pages/CalendarPage'
import TodosPage from './pages/TodosPage'
import MemosPage from './pages/MemosPage'
import FinancePage from './pages/FinancePage'
import EmailsPage from './pages/EmailsPage'
import FilesPage from './pages/FilesPage'
import PCsPage from './pages/PCsPage'
import ReportsPage from './pages/ReportsPage'
import IntegrationsPage from './pages/IntegrationsPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/managers" element={<ManagersPage />} />
        <Route path="/calendar" element={<CalendarPage />} />
        <Route path="/todos" element={<TodosPage />} />
        <Route path="/memos" element={<MemosPage />} />
        <Route path="/finance" element={<FinancePage />} />
        <Route path="/emails" element={<EmailsPage />} />
        <Route path="/files" element={<FilesPage />} />
        <Route path="/pcs" element={<PCsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/integrations" element={<IntegrationsPage />} />
      </Route>
    </Routes>
  )
}
