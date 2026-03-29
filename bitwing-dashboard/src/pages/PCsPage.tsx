/** PC 관리 페이지 */

import { useEffect, useState } from 'react'
import { Card, Table, Tag, Typography, Badge } from 'antd'
import { getPCs } from '../services/api'
import type { ManagedPC } from '../types'

const { Title } = Typography
const statusMap: Record<string, { color: string; text: string }> = {
  online: { color: 'green', text: '온라인' },
  offline: { color: 'default', text: '오프라인' },
  maintenance: { color: 'orange', text: '유지보수' },
}

export default function PCsPage() {
  const [pcs, setPCs] = useState<ManagedPC[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true)
    try {
      const res = await getPCs()
      setPCs(res.data.data?.items ?? [])
    } catch { /* empty */ } finally { setLoading(false) }
  }

  const columns = [
    {
      title: '상태', dataIndex: 'status', key: 'status', width: 100,
      render: (s: string) => <Badge status={s === 'online' ? 'processing' : 'default'} text={statusMap[s]?.text ?? s} />,
    },
    { title: '호스트명', dataIndex: 'hostname', key: 'hostname' },
    { title: 'IP', dataIndex: 'ip_address', key: 'ip_address' },
    { title: 'OS', dataIndex: 'os_type', key: 'os_type', render: (v: string) => <Tag>{v}</Tag> },
    { title: '사용자', dataIndex: 'employee_name', key: 'employee_name' },
    { title: '부서', dataIndex: 'department', key: 'department' },
    { title: '마지막 접속', dataIndex: 'last_seen_at', key: 'last_seen_at' },
  ]

  return (
    <>
      <Title level={4}>PC 관리</Title>
      <Card>
        <Table dataSource={pcs} columns={columns} rowKey="id" loading={loading} />
      </Card>
    </>
  )
}
