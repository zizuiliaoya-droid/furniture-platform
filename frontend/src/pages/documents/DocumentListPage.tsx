import { useEffect, useState } from 'react';
import { Button, Card, Input, message, Space, Table, Tag, Tree, Typography, Upload } from 'antd';
import { DownloadOutlined, UploadOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { documentService } from '../../services/documentService';
import { useAuthStore } from '../../store/authStore';

const { Title } = Typography;
const DOC_TYPE_MAP: Record<string, string> = { design: 'DESIGN', training: 'TRAINING', certificates: 'CERTIFICATE' };
const DOC_TYPE_LABEL: Record<string, string> = { DESIGN: '设计资源', TRAINING: '培训资料', CERTIFICATE: '资质文件' };

export default function DocumentListPage() {
  const { docType } = useParams();
  const apiDocType = DOC_TYPE_MAP[docType || ''] || 'DESIGN';
  const [documents, setDocuments] = useState<any[]>([]);
  const [folders, setFolders] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);
  const isAdmin = useAuthStore((s) => s.user?.role === 'ADMIN');

  const fetchDocs = async (params?: any) => {
    setLoading(true);
    try {
      const { data } = await documentService.getDocuments({ doc_type: apiDocType, folder: selectedFolder, ...params });
      setDocuments(data.results || data);
    } finally { setLoading(false); }
  };

  useEffect(() => {
    fetchDocs();
    documentService.getFolderTree(apiDocType).then(({ data }) => setFolders(data));
  }, [apiDocType, selectedFolder]);

  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', apiDocType);
    if (selectedFolder) formData.append('folder', String(selectedFolder));
    await documentService.uploadDocument(formData);
    message.success('上传成功');
    fetchDocs();
    return false;
  };

  const handleDownload = async (doc: any) => {
    const { data } = await documentService.downloadDocument(doc.id);
    const url = URL.createObjectURL(data);
    const a = document.createElement('a');
    a.href = url; a.download = doc.name; a.click();
    URL.revokeObjectURL(url);
  };

  const toTreeData = (nodes: any[]): any[] =>
    nodes.map((n) => ({ key: n.id, title: n.name, children: toTreeData(n.children || []) }));

  return (
    <div style={{ display: 'flex', gap: 16 }}>
      <Card title="文件夹" style={{ width: 240, flexShrink: 0 }} size="small">
        <Tree treeData={toTreeData(folders)} onSelect={(keys) => setSelectedFolder(keys[0] as number || null)} />
      </Card>
      <div style={{ flex: 1 }}>
        <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
          <Title level={4} style={{ margin: 0 }}>{DOC_TYPE_LABEL[apiDocType]}</Title>
          {isAdmin && <Upload beforeUpload={handleUpload} showUploadList={false}>
            <Button icon={<UploadOutlined />} type="primary">上传文档</Button>
          </Upload>}
        </Space>
        <Input.Search placeholder="搜索文件名..." allowClear style={{ marginBottom: 16, width: 300 }}
          onSearch={(v) => fetchDocs({ search: v })} />
        <Table dataSource={documents} rowKey="id" loading={loading} columns={[
          { title: '文件名', dataIndex: 'name' },
          { title: '大小', dataIndex: 'file_size', render: (v: number) => `${(v / 1024).toFixed(1)} KB` },
          { title: '标签', dataIndex: 'tags', render: (tags: string[]) => tags?.map((t) => <Tag key={t}>{t}</Tag>) },
          { title: '操作', render: (_: any, r: any) => <Button size="small" icon={<DownloadOutlined />} onClick={() => handleDownload(r)}>下载</Button> },
        ]} />
      </div>
    </div>
  );
}
