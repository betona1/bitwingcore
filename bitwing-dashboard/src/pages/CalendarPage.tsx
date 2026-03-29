/** 일정 관리 페이지 */

import { useEffect, useState } from 'react'
import { Card, Table, Button, Modal, Form, Input, DatePicker, Typography, Tag, Space, message } from 'antd'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { getCalendars, createCalendar, deleteCalendar } from '../services/api'
import type { CalendarEvent } from '../types'

const { Title } = Typography
const { RangePicker } = DatePicker

export default function CalendarPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => { load() }, [])

  const load = async (range = '이번주') => {
    setLoading(true)
    try {
      const res = await getCalendars(range)
      setEvents(res.data.data?.items ?? [])
    } catch { /* empty */ } finally { setLoading(false) }
  }

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()
      const [start, end] = values.dateRange
      await createCalendar({
        title: values.title,
        description: values.description,
        start_at: start.toISOString(),
        end_at: end.toISOString(),
        location: values.location,
      })
      message.success('일정을 등록했습니다.')
      setModalOpen(false)
      form.resetFields()
      load()
    } catch { /* validation */ }
  }

  const handleDelete = async (id: number) => {
    await deleteCalendar(id)
    message.success('일정을 삭제했습니다.')
    load()
  }

  const columns = [
    { title: '제목', dataIndex: 'title', key: 'title' },
    {
      title: '시작', dataIndex: 'start_at', key: 'start_at',
      render: (v: string) => dayjs(v).format('MM/DD HH:mm'),
    },
    {
      title: '종료', dataIndex: 'end_at', key: 'end_at',
      render: (v: string) => dayjs(v).format('MM/DD HH:mm'),
    },
    { title: '장소', dataIndex: 'location', key: 'location' },
    {
      title: '상태', dataIndex: 'status', key: 'status',
      render: (s: string) => <Tag color={s === 'active' ? 'green' : 'red'}>{s}</Tag>,
    },
    {
      title: '', key: 'actions',
      render: (_: unknown, record: CalendarEvent) => (
        <Button danger icon={<DeleteOutlined />} size="small" onClick={() => handleDelete(record.id)} />
      ),
    },
  ]

  return (
    <>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>일정 관리</Title>
        <Space>
          {['오늘', '이번주', '이번달'].map((r) => (
            <Button key={r} onClick={() => load(r)}>{r}</Button>
          ))}
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>새 일정</Button>
        </Space>
      </Space>
      <Card>
        <Table dataSource={events} columns={columns} rowKey="id" loading={loading} />
      </Card>

      <Modal title="일정 등록" open={modalOpen} onOk={handleCreate} onCancel={() => setModalOpen(false)} okText="등록">
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="제목" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="dateRange" label="일시" rules={[{ required: true }]}><RangePicker showTime /></Form.Item>
          <Form.Item name="location" label="장소"><Input /></Form.Item>
          <Form.Item name="description" label="설명"><Input.TextArea rows={2} /></Form.Item>
        </Form>
      </Modal>
    </>
  )
}
