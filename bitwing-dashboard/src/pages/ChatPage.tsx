/** 채팅 페이지 — AI 비서와 자연어 대화 */

import { useState, useRef, useEffect } from 'react'
import { Card, Input, Button, List, Typography, Tag, Space } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import { postChat } from '../services/api'
import { useAppStore } from '../stores/appStore'
import type { ChatMessage } from '../types'

const { Text, Paragraph } = Typography

export default function ChatPage() {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const { chatMessages, addChatMessage } = useAppStore()
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    listRef.current?.scrollTo(0, listRef.current.scrollHeight)
  }, [chatMessages])

  const handleSend = async () => {
    const msg = input.trim()
    if (!msg) return

    const userMsg: ChatMessage = { role: 'user', content: msg, timestamp: new Date().toISOString() }
    addChatMessage(userMsg)
    setInput('')
    setLoading(true)

    try {
      const res = await postChat(msg)
      const data = res.data.data
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: data?.response ?? res.data.message,
        timestamp: new Date().toISOString(),
        intent: data?.intent,
        manager: data?.manager,
      }
      addChatMessage(assistantMsg)
    } catch {
      addChatMessage({
        role: 'assistant',
        content: '서버 연결에 실패했습니다.',
        timestamp: new Date().toISOString(),
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card title="AI 비서 채팅" style={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
      <div ref={listRef} style={{ flex: 1, overflow: 'auto', marginBottom: 16, maxHeight: 'calc(100vh - 360px)' }}>
        <List
          dataSource={chatMessages}
          renderItem={(item) => (
            <List.Item style={{ justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start', border: 'none' }}>
              <div
                style={{
                  maxWidth: '70%',
                  padding: '8px 16px',
                  borderRadius: 12,
                  background: item.role === 'user' ? '#1677ff' : '#f0f0f0',
                  color: item.role === 'user' ? '#fff' : '#000',
                }}
              >
                <Paragraph style={{ margin: 0, color: 'inherit', whiteSpace: 'pre-wrap' }}>
                  {item.content}
                </Paragraph>
                {item.intent && (
                  <Space size={4} style={{ marginTop: 4 }}>
                    <Tag color="blue" style={{ fontSize: 10 }}>{item.intent}</Tag>
                    {item.manager && <Tag color="green" style={{ fontSize: 10 }}>{item.manager}</Tag>}
                  </Space>
                )}
                <div style={{ textAlign: 'right', marginTop: 2 }}>
                  <Text type="secondary" style={{ fontSize: 10, color: item.role === 'user' ? '#ccc' : undefined }}>
                    {new Date(item.timestamp).toLocaleTimeString('ko-KR')}
                  </Text>
                </div>
              </div>
            </List.Item>
          )}
        />
      </div>
      <Space.Compact style={{ width: '100%' }}>
        <Input
          placeholder="메시지를 입력하세요... (예: 오늘 할일 보여줘)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onPressEnter={handleSend}
          disabled={loading}
          size="large"
        />
        <Button type="primary" icon={<SendOutlined />} onClick={handleSend} loading={loading} size="large" />
      </Space.Compact>
    </Card>
  )
}
