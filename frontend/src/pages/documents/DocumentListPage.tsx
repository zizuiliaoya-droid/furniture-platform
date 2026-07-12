import { useEffect, useState } from 'react';
import {
  Button, Card, Form, Input, Modal, message, Popconfirm, Space, Table, Tag, Tree, Typography, Upload,
} from 'antd';
import {
  DownloadOutlined, EditOutlined, EyeOutlined, FileTextOutlined, UploadOutlined, DeleteOutlined,
} from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { documentService } from '../../services/documentService';
import { useAuthStore } from '../../store/authStore';
import MediaPreview from '../../components/MediaPreview';

const { Title, Text } = Typography;
const { TextArea } = Input;
const DOC_TYPE_MAP: Record<string, string> = { design: 'DESIGN', training: 'TRAINING', certificates: 'CERTIFICATE' };
const DOC_TYPE_LABEL: Record<string, string> = { DESIGN: '设计资源', TRAINING: '培训资料', CERTIFICATE: '资质文件' };

export default function DocumentListPage() {
  const { docType } = useParams();
  const apiDocType = DOC_TYPE_MAP[docType || ''] || 'DESIGN';
  const [documents, setDocuments] = useState<any[]>([]);
  const [folders, setFolders] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);
  const [richTextOpen, setRichTextOpen] = useState(false);
  const [editingRichText, setEditingRichText] = useState<any>(null);
  const [richTextForm] = Form.useForm();
  const isAdmin = useAuthStore((s) => s.user?.role === 'ADMIN');
  const isTraining = apiDocType === 'TRAINING';

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

  const handleDeleteDoc = async (doc: any) => {
    try {
      await documentService.deleteDocument(doc.id);
      message.success('已删除');
      fetchDocs();
    } catch {
      message.error('删除失败');
    }
  };

  const [folderModalOpen, setFolderModalOpen] = useState(false);
  const [folderName, setFolderName] = useState('');
  const reloadFolders = () => documentService.getFolderTree(apiDocType).then(({ data }) => setFolders(data));

  const handleCreateFolder = async () => {
    if (!folderName.trim()) { message.error('请输入文件夹名称'); return; }
    try {
      await documentService.createFolder({ name: folderName.trim(), doc_type: apiDocType, parent: selectedFolder });
      message.success('文件夹已创建');
      setFolderModalOpen(false);
      setFolderName('');
      reloadFolders();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '创建失败');
    }
  };

  const handleDeleteFolder = async () => {
    if (!selectedFolder) return;
    try {
      await documentService.deleteFolder(selectedFolder);
      message.success('文件夹已删除');
      setSelectedFolder(null);
      reloadFolders();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '删除失败（可能含文件或子文件夹）');
    }
  };

  const openRichTextEditor = (doc?: any) => {
    setEditingRichText(doc || null);
    richTextForm.setFieldsValue({
      name: doc?.name || '',
      content: doc?.content || '',
      tags: (doc?.tags || []).join(','),
    });
    setRichTextOpen(true);
  };

  const handleRichTextSubmit = async () => {
    try {
      const values = await richTextForm.validateFields();
      const payload = {
        name: values.name,
        content: values.content,
        doc_type: apiDocType,
        folder: selectedFolder,
        tags: (values.tags || '').split(',').map((t: string) => t.trim()).filter(Boolean),
      };
      if (editingRichText) {
        await documentService.updateRichText(editingRichText.id, payload);
        message.success('已更新');
      } else {
        await documentService.createRichText(payload);
        message.success('已创建');
      }
      setRichTextOpen(false);
      setEditingRichText(null);
      richTextForm.resetFields();
      fetchDocs();
    } catch (err: any) {
      if (err.response) {
        message.error(err.response?.data?.detail || '保存失败');
      }
    }
  };

  const canPreview = (doc: any) => {
    if (doc.resource_type === 'RICH_TEXT') return true;
    const m = doc.mime_type || '';
    return m.startsWith('image/') || m === 'application/pdf' ||
      m.startsWith('video/') || m.startsWith('audio/') ||
      /\.(doc|docx|ppt|pptx|xls|xlsx)$/i.test(doc.name);
  };

  const toTreeData = (nodes: any[]): any[] =>
    nodes.map((n) => ({ key: n.id, title: n.name, children: toTreeData(n.children || []) }));

  return (
    <div style={{ display: 'flex', gap: 16 }}>
      <Card title="文件夹" style={{ width: 240, flexShrink: 0 }} size="small"
        extra={isAdmin && (
          <Space size={4}>
            <Button size="small" type="link" onClick={() => setFolderModalOpen(true)}>新建</Button>
            {selectedFolder && (
              <Popconfirm title="删除该文件夹？" okText="删除" cancelText="取消"
                okButtonProps={{ danger: true }} onConfirm={handleDeleteFolder}>
                <Button size="small" type="link" danger>删除</Button>
              </Popconfirm>
            )}
          </Space>
        )}
      >
        <Tree treeData={toTreeData(folders)}
          selectedKeys={selectedFolder ? [selectedFolder] : []}
          onSelect={(keys) => setSelectedFolder(keys[0] as number || null)} />
      </Card>

      <Modal
        title="新建文件夹"
        open={folderModalOpen}
        onCancel={() => { setFolderModalOpen(false); setFolderName(''); }}
        onOk={handleCreateFolder}
        okText="创建"
      >
        <Input placeholder="文件夹名称" value={folderName} onChange={(e) => setFolderName(e.target.value)} />
        {selectedFolder && <Text type="secondary">将创建在当前选中文件夹下</Text>}
      </Modal>
      <div style={{ flex: 1 }}>
        <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
          <Title level={4} style={{ margin: 0 }}>{DOC_TYPE_LABEL[apiDocType]}</Title>
          {isAdmin && (
            <Space>
              {isTraining && (
                <Button icon={<FileTextOutlined />} onClick={() => openRichTextEditor()}>
                  新建富文本
                </Button>
              )}
              <Upload beforeUpload={handleUpload} showUploadList={false}>
                <Button icon={<UploadOutlined />} type="primary">上传文档</Button>
              </Upload>
            </Space>
          )}
        </Space>
        <Input.Search placeholder="搜索文件名..." allowClear style={{ marginBottom: 16, width: 300 }}
          onSearch={(v) => fetchDocs({ search: v })} />
        <Table
          dataSource={documents}
          rowKey="id"
          loading={loading}
          columns={[
            {
              title: '文件名', dataIndex: 'name', ellipsis: true,
              render: (text: string, r: any) => (
                <Space>
                  {r.resource_type === 'RICH_TEXT' && <FileTextOutlined style={{ color: '#1890ff' }} />}
                  <span>{text}</span>
                </Space>
              ),
            },
            { title: '类型', dataIndex: 'mime_type', width: 120, ellipsis: true,
              render: (m: string, r: any) => r.resource_type === 'RICH_TEXT' ? '富文本' : m },
            {
              title: '大小', dataIndex: 'file_size', width: 100,
              render: (v: number, r: any) => r.resource_type === 'RICH_TEXT'
                ? `${(r.content?.length || 0)} 字符`
                : (v > 1048576 ? `${(v / 1048576).toFixed(1)} MB` : `${(v / 1024).toFixed(1)} KB`),
            },
            { title: '标签', dataIndex: 'tags', render: (tags: string[]) => tags?.map((t) => <Tag key={t}>{t}</Tag>) },
            {
              title: '操作', width: 200,
              render: (_: any, r: any) => (
                <Space size="small">
                  {canPreview(r) && (
                    <MediaPreview
                      filePath={r.file_path}
                      mimeType={r.mime_type || ''}
                      fileName={r.name}
                      isRichText={r.resource_type === 'RICH_TEXT'}
                      richTextContent={r.content}
                      trigger={<Button size="small" icon={<EyeOutlined />}>预览</Button>}
                    />
                  )}
                  {r.resource_type === 'RICH_TEXT' && isAdmin && (
                    <Button size="small" icon={<EditOutlined />} onClick={() => openRichTextEditor(r)}>编辑</Button>
                  )}
                  {r.resource_type !== 'RICH_TEXT' && (
                    <Button size="small" icon={<DownloadOutlined />} onClick={() => handleDownload(r)}>下载</Button>
                  )}
                  {isAdmin && (
                    <Popconfirm
                      title="确认删除该文件？"
                      okText="删除"
                      cancelText="取消"
                      okButtonProps={{ danger: true }}
                      onConfirm={() => handleDeleteDoc(r)}
                    >
                      <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
                    </Popconfirm>
                  )}
                </Space>
              ),
            },
          ]}
        />
      </div>

      <Modal
        title={editingRichText ? '编辑富文本' : '新建富文本'}
        open={richTextOpen}
        onCancel={() => { setRichTextOpen(false); setEditingRichText(null); }}
        onOk={handleRichTextSubmit}
        width={720}
        okText="保存"
      >
        <Form form={richTextForm} layout="vertical">
          <Form.Item name="name" label="标题" rules={[{ required: true, message: '请输入标题' }]}>
            <Input placeholder="文档标题" />
          </Form.Item>
          <Form.Item name="content" label="内容（HTML）" rules={[{ required: true, message: '请输入内容' }]}>
            <TextArea
              rows={14}
              placeholder='可粘贴 HTML，例如：<h2>标题</h2><p>段落</p><img src="..." /><video src="..." controls></video>'
            />
          </Form.Item>
          <Form.Item name="tags" label="标签（逗号分隔）">
            <Input placeholder="如: 入门, 视频教程" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
