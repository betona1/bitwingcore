/** 파일 관리 페이지 */

import { useEffect, useState } from 'react'
import { Card, Table, Tag, Typography } from 'antd'
import { getFiles } from '../services/api'

const { Title } = Typography

interface FileItem {
  id: number; filename: string; filepath: string; file_size?: number;
  mime_type?: string; category?: string; access_level: string; created_at: string;
}

export default function FilesPage() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true)
    try {
      const res = await getFiles()
      setFiles(res.data.data?.items ?? [])
    } catch { /* empty */ } finally { setLoading(false) }
  }

  const formatSize = (bytes?: number) => {
    if (!bytes) return '-'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / 1048576).toFixed(1)} MB`
  }

  const columns = [
    { title: '파일명', dataIndex: 'filename', key: 'filename' },
    { title: '크기', dataIndex: 'file_size', key: 'file_size', render: formatSize },
    { title: '타입', dataIndex: 'mime_type', key: 'mime_type' },
    { title: '카테고리', dataIndex: 'category', key: 'category' },
    {
      title: '접근', dataIndex: 'access_level', key: 'access_level',
      render: (v: string) => <Tag color={v === 'public' ? 'green' : v === 'private' ? 'red' : 'orange'}>{v}</Tag>,
    },
    { title: '등록일', dataIndex: 'created_at', key: 'created_at' },
  ]

  return (
    <>
      <Title level={4}>파일 관리</Title>
      <Card><Table dataSource={files} columns={columns} rowKey="id" loading={loading} /></Card>
    </>
  )
}
