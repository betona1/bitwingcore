/** 이메일 페이지 */

import { useEffect, useState } from 'react'
import { Card, Table, Tag, Typography, Switch, Space } from 'antd'
import { getEmails } from '../services/api'
import type { EmailItem } from '../types'

const { Title } = Typography

export default function EmailsPage() {
  const [emails, setEmails] = useState<EmailItem[]>([])
  const [loading, setLoading] = useState(true)
  const [unreadOnly, setUnreadOnly] = useState(false)

  useEffect(() => { load() }, [unreadOnly])

  const load = async () => {
    setLoading(true)
    try {
      const res = await getEmails({ unread_only: unreadOnly })
      setEmails(res.data.data?.items ?? [])
    } catch { /* empty */ } finally { setLoading(false) }
  }

  const columns = [
    {
      title: '', dataIndex: 'is_read', key: 'is_read', width: 40,
      render: (v: boolean) => v ? null : <Tag color="blue">NEW</Tag>,
    },
    { title: '보낸 사람', dataIndex: 'sender', key: 'sender', width: 200 },
    { title: '제목', dataIndex: 'subject', key: 'subject' },
    { title: '수신일', dataIndex: 'received_at', key: 'received_at', width: 160 },
    { title: '제공자', dataIndex: 'provider', key: 'provider', width: 100, render: (v: string) => <Tag>{v}</Tag> },
  ]

  return (
    <>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>이메일</Title>
        <Space>
          <span>읽지 않은 메일만</span>
          <Switch checked={unreadOnly} onChange={setUnreadOnly} />
        </Space>
      </Space>
      <Card>
        <Table dataSource={emails} columns={columns} rowKey="id" loading={loading} />
      </Card>
    </>
  )
}
