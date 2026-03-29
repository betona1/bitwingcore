/** 매니저 관리 페이지 */

import { useEffect, useState } from 'react'
import { Card, Table, Tag, Typography, Spin, Badge } from 'antd'
import { getManagers } from '../services/api'
import type { Manager } from '../types'

const { Title } = Typography

const statusColor: Record<string, string> = {
  active: 'green',
  busy: 'orange',
  idle: 'blue',
  disabled: 'red',
}

export default function ManagersPage() {
  const [managers, setManagers] = useState<Manager[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadManagers()
  }, [])

  const loadManagers = async () => {
    try {
      const res = await getManagers()
      setManagers(res.data.data ?? [])
    } catch {
      // 서버 미연결
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    {
      title: '매니저',
      dataIndex: 'display_name',
      key: 'display_name',
      render: (text: string, record: Manager) => (
        <span>
          <Badge status={record.status === 'active' ? 'processing' : 'default'} />
          {text}
        </span>
      ),
    },
    { title: '코드명', dataIndex: 'code_name', key: 'code_name' },
    { title: '역할', dataIndex: 'role', key: 'role' },
    {
      title: '담당 모듈',
      dataIndex: 'managed_modules',
      key: 'managed_modules',
      render: (modules: string[]) =>
        modules?.map((m) => <Tag key={m} color="blue">{m}</Tag>),
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      render: (s: string) => <Tag color={statusColor[s] ?? 'default'}>{s ?? 'idle'}</Tag>,
    },
    {
      title: '처리 건수',
      dataIndex: 'total_tasks',
      key: 'total_tasks',
      render: (v: number) => v ?? 0,
    },
  ]

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <>
      <Title level={4}>AI 매니저 관리</Title>
      <Card>
        <Table
          dataSource={managers}
          columns={columns}
          rowKey="code_name"
          pagination={false}
        />
      </Card>
    </>
  )
}
