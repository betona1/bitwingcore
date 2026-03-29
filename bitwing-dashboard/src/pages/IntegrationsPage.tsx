/** 연동 관리 페이지 */

import { useEffect, useState } from 'react'
import { Card, Table, Tag, Typography } from 'antd'
import { getIntegrations } from '../services/api'

const { Title } = Typography

interface IntegrationItem {
  id: number; service: string; status: string; last_synced_at?: string;
}

const statusColor: Record<string, string> = {
  connected: 'green', disconnected: 'default', error: 'red',
}

export default function IntegrationsPage() {
  const [items, setItems] = useState<IntegrationItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true)
    try {
      const res = await getIntegrations()
      setItems(res.data.data?.items ?? [])
    } catch { /* empty */ } finally { setLoading(false) }
  }

  const columns = [
    { title: '서비스', dataIndex: 'service', key: 'service' },
    {
      title: '상태', dataIndex: 'status', key: 'status',
      render: (s: string) => <Tag color={statusColor[s] ?? 'default'}>{s}</Tag>,
    },
    { title: '마지막 동기화', dataIndex: 'last_synced_at', key: 'last_synced_at' },
  ]

  return (
    <>
      <Title level={4}>외부 연동</Title>
      <Card><Table dataSource={items} columns={columns} rowKey="id" loading={loading} /></Card>
    </>
  )
}
