/** 할일 관리 페이지 */

import { useEffect, useState } from 'react'
import { Card, Table, Button, Modal, Form, Input, Select, DatePicker, Tag, Space, Typography, message } from 'antd'
import { PlusOutlined, CheckOutlined, DeleteOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { getTodos, createTodo, completeTodo, deleteTodo } from '../services/api'
import type { Todo } from '../types'

const { Title } = Typography

const priorityColor: Record<string, string> = { urgent: 'red', high: 'orange', normal: 'blue', low: 'default' }
const statusLabel: Record<string, string> = { pending: '대기', in_progress: '진행', completed: '완료', cancelled: '취소' }

export default function TodosPage() {
  const [todos, setTodos] = useState<Todo[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [filter, setFilter] = useState<string | undefined>(undefined)
  const [form] = Form.useForm()

  useEffect(() => { load() }, [filter])

  const load = async () => {
    setLoading(true)
    try {
      const res = await getTodos({ status: filter })
      setTodos(res.data.data?.items ?? [])
    } catch { /* empty */ } finally { setLoading(false) }
  }

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()
      await createTodo({
        title: values.title,
        description: values.description,
        priority: values.priority ?? 'normal',
        due_date: values.due_date?.format('YYYY-MM-DD'),
      })
      message.success('할일을 등록했습니다.')
      setModalOpen(false)
      form.resetFields()
      load()
    } catch { /* empty */ }
  }

  const columns = [
    { title: '제목', dataIndex: 'title', key: 'title' },
    {
      title: '우선순위', dataIndex: 'priority', key: 'priority',
      render: (p: string) => <Tag color={priorityColor[p]}>{p}</Tag>,
    },
    {
      title: '상태', dataIndex: 'status', key: 'status',
      render: (s: string) => <Tag>{statusLabel[s] ?? s}</Tag>,
    },
    {
      title: '마감일', dataIndex: 'due_date', key: 'due_date',
      render: (v: string) => v ? dayjs(v).format('MM/DD') : '-',
    },
    {
      title: '', key: 'actions',
      render: (_: unknown, r: Todo) => (
        <Space>
          {r.status !== 'completed' && (
            <Button icon={<CheckOutlined />} size="small" onClick={async () => { await completeTodo(r.id); load() }} />
          )}
          <Button danger icon={<DeleteOutlined />} size="small" onClick={async () => { await deleteTodo(r.id); load() }} />
        </Space>
      ),
    },
  ]

  return (
    <>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>할일 관리</Title>
        <Space>
          <Select placeholder="상태 필터" allowClear onChange={setFilter} style={{ width: 120 }}
            options={[
              { value: 'pending', label: '대기' },
              { value: 'in_progress', label: '진행중' },
              { value: 'completed', label: '완료' },
            ]}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>새 할일</Button>
        </Space>
      </Space>
      <Card>
        <Table dataSource={todos} columns={columns} rowKey="id" loading={loading} />
      </Card>

      <Modal title="할일 등록" open={modalOpen} onOk={handleCreate} onCancel={() => setModalOpen(false)} okText="등록">
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="제목" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="priority" label="우선순위" initialValue="normal">
            <Select options={[{ value: 'urgent', label: '긴급' }, { value: 'high', label: '높음' }, { value: 'normal', label: '보통' }, { value: 'low', label: '낮음' }]} />
          </Form.Item>
          <Form.Item name="due_date" label="마감일"><DatePicker /></Form.Item>
          <Form.Item name="description" label="설명"><Input.TextArea rows={2} /></Form.Item>
        </Form>
      </Modal>
    </>
  )
}
