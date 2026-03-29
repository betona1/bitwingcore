/** 가계부 페이지 — 거래 내역 + 요약 차트 */

import { useEffect, useState } from 'react'
import { Card, Table, Button, Modal, Form, Input, Select, DatePicker, InputNumber, Row, Col, Statistic, Typography, Tag, Space, message } from 'antd'
import { PlusOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import dayjs from 'dayjs'
import { getTransactions, getFinanceSummary, createTransaction } from '../services/api'
import type { FinanceTransaction, FinanceSummary } from '../types'

const { Title } = Typography

export default function FinancePage() {
  const [transactions, setTransactions] = useState<FinanceTransaction[]>([])
  const [summary, setSummary] = useState<FinanceSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [period, setPeriod] = useState('이번달')
  const [form] = Form.useForm()

  useEffect(() => { load() }, [period])

  const load = async () => {
    setLoading(true)
    try {
      const [txRes, sumRes] = await Promise.allSettled([
        getTransactions({ date_range: period }),
        getFinanceSummary(period),
      ])
      if (txRes.status === 'fulfilled') setTransactions(txRes.value.data.data?.items ?? [])
      if (sumRes.status === 'fulfilled') setSummary(sumRes.value.data.data ?? null)
    } catch { /* empty */ } finally { setLoading(false) }
  }

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()
      await createTransaction({
        type: values.type,
        amount: values.amount,
        category: values.category,
        description: values.description,
        payment_method: values.payment_method,
        transaction_date: values.transaction_date.format('YYYY-MM-DD'),
      })
      message.success('거래를 기록했습니다.')
      setModalOpen(false)
      form.resetFields()
      load()
    } catch { /* empty */ }
  }

  const chartData = summary?.expense_by_category
    ? Object.entries(summary.expense_by_category).map(([name, value]) => ({ name, amount: value }))
    : []

  const columns = [
    {
      title: '구분', dataIndex: 'type', key: 'type',
      render: (t: string) => <Tag color={t === 'income' ? 'green' : 'red'}>{t === 'income' ? '수입' : '지출'}</Tag>,
    },
    { title: '카테고리', dataIndex: 'category', key: 'category' },
    {
      title: '금액', dataIndex: 'amount', key: 'amount',
      render: (v: number) => `${v.toLocaleString()}원`,
    },
    { title: '설명', dataIndex: 'description', key: 'description' },
    { title: '일자', dataIndex: 'transaction_date', key: 'transaction_date' },
  ]

  return (
    <>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>가계부</Title>
        <Space>
          {['이번주', '이번달', '지난달'].map((r) => (
            <Button key={r} type={period === r ? 'primary' : 'default'} onClick={() => setPeriod(r)}>{r}</Button>
          ))}
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>기록</Button>
        </Space>
      </Space>

      {summary && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={8}>
            <Card><Statistic title="수입" value={summary.total_income} suffix="원" prefix={<ArrowUpOutlined />} valueStyle={{ color: '#3f8600' }} formatter={(v) => Number(v).toLocaleString()} /></Card>
          </Col>
          <Col span={8}>
            <Card><Statistic title="지출" value={summary.total_expense} suffix="원" prefix={<ArrowDownOutlined />} valueStyle={{ color: '#cf1322' }} formatter={(v) => Number(v).toLocaleString()} /></Card>
          </Col>
          <Col span={8}>
            <Card><Statistic title="잔액" value={summary.balance} suffix="원" formatter={(v) => Number(v).toLocaleString()} /></Card>
          </Col>
        </Row>
      )}

      {chartData.length > 0 && (
        <Card title="카테고리별 지출" style={{ marginBottom: 16 }}>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(v) => `${(v / 10000).toFixed(0)}만`} />
              <Tooltip formatter={(v) => `${Number(v).toLocaleString()}원`} />
              <Bar dataKey="amount" fill="#1677ff" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      <Card>
        <Table dataSource={transactions} columns={columns} rowKey="id" loading={loading} />
      </Card>

      <Modal title="거래 기록" open={modalOpen} onOk={handleCreate} onCancel={() => setModalOpen(false)} okText="저장">
        <Form form={form} layout="vertical" initialValues={{ type: 'expense', transaction_date: dayjs() }}>
          <Form.Item name="type" label="구분" rules={[{ required: true }]}>
            <Select options={[{ value: 'expense', label: '지출' }, { value: 'income', label: '수입' }]} />
          </Form.Item>
          <Form.Item name="amount" label="금액" rules={[{ required: true }]}><InputNumber style={{ width: '100%' }} min={1} /></Form.Item>
          <Form.Item name="category" label="카테고리" rules={[{ required: true }]}><Input placeholder="식비, 교통, 쇼핑 등" /></Form.Item>
          <Form.Item name="transaction_date" label="일자" rules={[{ required: true }]}><DatePicker style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="description" label="설명"><Input /></Form.Item>
          <Form.Item name="payment_method" label="결제수단"><Input placeholder="현금, 카드 등" /></Form.Item>
        </Form>
      </Modal>
    </>
  )
}
