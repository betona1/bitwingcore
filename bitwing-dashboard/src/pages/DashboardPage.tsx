/** 대시보드 홈 페이지 — 전체 요약 카드 + 차트 */

import { useEffect, useState } from 'react'
import { Card, Col, Row, Statistic, Typography, Spin } from 'antd'
import {
  CalendarOutlined,
  CheckSquareOutlined,
  DollarOutlined,
  TeamOutlined,
} from '@ant-design/icons'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { getManagers, getFinanceSummary, getTodos, getCalendars } from '../services/api'

const { Title } = Typography
const COLORS = ['#1677ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2']

export default function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    todaySchedules: 0,
    pendingTodos: 0,
    monthExpense: 0,
    activeManagers: 0,
  })
  const [expenseChart, setExpenseChart] = useState<{ name: string; value: number }[]>([])

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const [calRes, todoRes, finRes, mgrRes] = await Promise.allSettled([
        getCalendars('오늘'),
        getTodos({ status: 'pending' }),
        getFinanceSummary('이번달'),
        getManagers(),
      ])

      const calData = calRes.status === 'fulfilled' ? calRes.value.data.data : null
      const todoData = todoRes.status === 'fulfilled' ? todoRes.value.data.data : null
      const finData = finRes.status === 'fulfilled' ? finRes.value.data.data : null
      const mgrData = mgrRes.status === 'fulfilled' ? mgrRes.value.data.data : null

      setStats({
        todaySchedules: calData?.items?.length ?? 0,
        pendingTodos: todoData?.meta?.total ?? 0,
        monthExpense: finData?.total_expense ?? 0,
        activeManagers: mgrData?.length ?? 0,
      })

      if (finData?.expense_by_category) {
        const chartData = Object.entries(finData.expense_by_category).map(
          ([name, value]) => ({ name, value: value as number })
        )
        setExpenseChart(chartData)
      }
    } catch {
      // 서버 미연결 시 기본값 유지
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <>
      <Title level={4}>대시보드</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="오늘 일정" value={stats.todaySchedules} prefix={<CalendarOutlined />} suffix="건" />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="대기 할일" value={stats.pendingTodos} prefix={<CheckSquareOutlined />} suffix="건" />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="이번달 지출"
              value={stats.monthExpense}
              prefix={<DollarOutlined />}
              suffix="원"
              formatter={(v) => Number(v).toLocaleString()}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="AI 매니저" value={stats.activeManagers} prefix={<TeamOutlined />} suffix="명" />
          </Card>
        </Col>
      </Row>

      {expenseChart.length > 0 && (
        <Card title="이번달 카테고리별 지출" style={{ marginTop: 16 }}>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={expenseChart} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                {expenseChart.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => `${Number(v).toLocaleString()}원`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      )}
    </>
  )
}
