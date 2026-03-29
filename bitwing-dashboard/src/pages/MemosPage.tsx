/** 메모 관리 페이지 */

import { useEffect, useState } from 'react'
import { Card, List, Button, Modal, Form, Input, Tag, Space, Typography, message, Empty } from 'antd'
import { PlusOutlined, SearchOutlined, DeleteOutlined } from '@ant-design/icons'
import { getMemos, searchMemos, createMemo, deleteMemo } from '../services/api'
import type { Memo } from '../types'

const { Title, Paragraph, Text } = Typography

export default function MemosPage() {
  const [memos, setMemos] = useState<Memo[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [form] = Form.useForm()

  useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true)
    try {
      const res = await getMemos()
      setMemos(res.data.data?.items ?? [])
    } catch { /* empty */ } finally { setLoading(false) }
  }

  const handleSearch = async () => {
    if (!searchText.trim()) { load(); return }
    setLoading(true)
    try {
      const res = await searchMemos(searchText)
      setMemos(res.data.data?.items ?? [])
    } catch { /* empty */ } finally { setLoading(false) }
  }

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()
      await createMemo({ title: values.title, content: values.content, category: values.category })
      message.success('메모를 저장했습니다.')
      setModalOpen(false)
      form.resetFields()
      load()
    } catch { /* empty */ }
  }

  const handleDelete = async (id: number) => {
    await deleteMemo(id)
    message.success('메모를 삭제했습니다.')
    load()
  }

  return (
    <>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>메모</Title>
        <Space>
          <Input.Search placeholder="검색..." value={searchText} onChange={(e) => setSearchText(e.target.value)}
            onSearch={handleSearch} style={{ width: 250 }} enterButton={<SearchOutlined />} />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>새 메모</Button>
        </Space>
      </Space>

      {memos.length === 0 && !loading ? <Empty description="메모가 없습니다." /> : (
        <List
          grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3 }}
          loading={loading}
          dataSource={memos}
          renderItem={(memo) => (
            <List.Item>
              <Card
                title={memo.title ?? '무제'}
                extra={<Button danger size="small" icon={<DeleteOutlined />} onClick={() => handleDelete(memo.id)} />}
                size="small"
              >
                <Paragraph ellipsis={{ rows: 3 }}>{memo.content}</Paragraph>
                {memo.category && <Tag>{memo.category}</Tag>}
                <div><Text type="secondary" style={{ fontSize: 12 }}>{memo.created_at}</Text></div>
              </Card>
            </List.Item>
          )}
        />
      )}

      <Modal title="메모 작성" open={modalOpen} onOk={handleCreate} onCancel={() => setModalOpen(false)} okText="저장">
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="제목"><Input /></Form.Item>
          <Form.Item name="content" label="내용" rules={[{ required: true }]}><Input.TextArea rows={5} /></Form.Item>
          <Form.Item name="category" label="카테고리"><Input placeholder="업무, 개인 등" /></Form.Item>
        </Form>
      </Modal>
    </>
  )
}
