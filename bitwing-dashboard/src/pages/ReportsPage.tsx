/** 리포트 페이지 — 일일/주간/월간 */

import { useState } from 'react'
import { Card, Segmented, Typography, Button, Spin, Space } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { getDailyReport, getWeeklyReport, getMonthlyReport } from '../services/api'

const { Title, Paragraph } = Typography

export default function ReportsPage() {
  const [reportType, setReportType] = useState<string>('daily')
  const [reportText, setReportText] = useState('')
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const fn = { daily: getDailyReport, weekly: getWeeklyReport, monthly: getMonthlyReport }[reportType]
      if (!fn) return
      const res = await fn()
      setReportText(res.data.data?.report_text ?? '리포트 데이터가 없습니다.')
    } catch {
      setReportText('서버 연결에 실패했습니다.')
    } finally { setLoading(false) }
  }

  return (
    <>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>리포트</Title>
        <Space>
          <Segmented
            value={reportType}
            onChange={(v) => setReportType(v as string)}
            options={[
              { label: '일일', value: 'daily' },
              { label: '주간', value: 'weekly' },
              { label: '월간', value: 'monthly' },
            ]}
          />
          <Button icon={<ReloadOutlined />} onClick={load} type="primary">생성</Button>
        </Space>
      </Space>
      <Card>
        {loading ? (
          <Spin size="large" style={{ display: 'block', margin: '50px auto' }} />
        ) : reportText ? (
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: 14 }}>{reportText}</pre>
        ) : (
          <Paragraph type="secondary">"생성" 버튼을 눌러 리포트를 생성하세요.</Paragraph>
        )}
      </Card>
    </>
  )
}
