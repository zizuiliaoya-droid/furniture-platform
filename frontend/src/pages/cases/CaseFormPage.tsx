import { useEffect, useState } from 'react';
import { Button, Card, Divider, Form, Image, Input, message, Popconfirm, Select, Space, Tag, Typography, Upload } from 'antd';
import { DeleteOutlined, InboxOutlined, StarOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { caseService } from '../../services/caseService';

const { Title, Text } = Typography;
const { Dragger } = Upload;

const INDUSTRIES = [
  { value: 'TECH_OFFICE', label: '科技/互联网办公' },
  { value: 'FINANCE_OFFICE', label: '金融/保险/财税办公' },
  { value: 'REALESTATE_OFFICE', label: '地产/建筑/设计院' },
  { value: 'EDUCATION_OFFICE', label: '教育培训办公' },
  { value: 'MEDICAL_OFFICE', label: '医疗/大健康办公' },
  { value: 'MEDIA_OFFICE', label: '广告/文创/传媒办公' },
  { value: 'MANUFACTURE_OFFICE', label: '制造/实业/工厂办公' },
  { value: 'GOVERNMENT_OFFICE', label: '政府/国企/事业单位' },
  { value: 'OTHER', label: '其他' },
];

export default function CaseFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState<any[]>([]);
  const [pendingImages, setPendingImages] = useState<File[]>([]);
  const navigate = useNavigate();

  const loadImages = () => {
    if (id) caseService.getCase(Number(id)).then(({ data }) => setImages(data.images || []));
  };

  useEffect(() => {
    if (isEdit) {
      caseService.getCase(Number(id)).then(({ data }) => {
        form.setFieldsValue(data);
        setImages(data.images || []);
      });
    }
  }, [id]);

  const handleUploadExisting = async (file: File) => {
    if (!id) return;
    const fd = new FormData();
    fd.append('images', file);
    try {
      await caseService.uploadImages(Number(id), fd);
      message.success('图片上传成功');
      loadImages();
    } catch { message.error('图片上传失败'); }
  };

  const handleDeleteImage = async (imageId: number) => {
    try {
      await caseService.deleteImage(imageId);
      message.success('图片已删除');
      loadImages();
    } catch { message.error('删除失败'); }
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      if (isEdit) {
        await caseService.updateCase(Number(id), values);
        message.success('案例更新成功');
      } else {
        const { data: created } = await caseService.createCase(values);
        if (pendingImages.length) {
          const fd = new FormData();
          pendingImages.forEach((f) => fd.append('images', f));
          try { await caseService.uploadImages(created.id, fd); }
          catch { message.warning('案例已创建，但部分图片上传失败'); }
        }
        message.success('案例创建成功');
      }
      navigate('/cases');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '操作失败');
    } finally { setLoading(false); }
  };

  return (
    <div style={{ maxWidth: 720 }}>
      <Title level={4}>{isEdit ? '编辑案例' : '新建案例'}</Title>
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item name="title" label="案例标题" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="industry" label="行业分类" rules={[{ required: true }]}>
          <Select options={INDUSTRIES} />
        </Form.Item>
        <Form.Item name="description" label="项目描述"><Input.TextArea rows={4} /></Form.Item>

        <Divider orientation="left">案例图片</Divider>
        {isEdit ? (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Dragger accept="image/*" multiple showUploadList={false}
              beforeUpload={(file) => { handleUploadExisting(file); return false; }}>
              <p className="ant-upload-drag-icon"><InboxOutlined /></p>
              <p>点击或拖拽上传案例图片</p>
            </Dragger>
            {images.length > 0 && (
              <Image.PreviewGroup>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                  {images.map((img: any) => (
                    <div key={img.id} style={{ border: '1px solid #f0f0f0', borderRadius: 4, padding: 4, width: 130 }}>
                      <Image width={118} height={118} style={{ objectFit: 'cover', borderRadius: 4 }}
                        src={`/media/${img.thumbnail_path?.medium || img.image_path}`} />
                      <div style={{ textAlign: 'center', marginTop: 4 }}>
                        {img.is_cover && <Tag color="blue"><StarOutlined /> 封面</Tag>}
                        <Popconfirm title="删除该图片？" okText="删除" cancelText="取消"
                          okButtonProps={{ danger: true }} onConfirm={() => handleDeleteImage(img.id)}>
                          <Button size="small" type="link" danger icon={<DeleteOutlined />} />
                        </Popconfirm>
                      </div>
                    </div>
                  ))}
                </div>
              </Image.PreviewGroup>
            )}
          </Space>
        ) : (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Dragger accept="image/*" multiple showUploadList={false}
              beforeUpload={(file) => { setPendingImages((prev) => [...prev, file]); return false; }}>
              <p className="ant-upload-drag-icon"><InboxOutlined /></p>
              <p>点击或拖拽添加图片（保存时随案例一起上传）</p>
            </Dragger>
            {pendingImages.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {pendingImages.map((f, i) => (
                  <div key={i} style={{ width: 90 }}>
                    <img src={URL.createObjectURL(f)} alt="" style={{ width: 88, height: 88, objectFit: 'cover', borderRadius: 4 }} />
                    <Button size="small" danger type="link" icon={<DeleteOutlined />}
                      onClick={() => setPendingImages((prev) => prev.filter((_, idx) => idx !== i))} />
                  </div>
                ))}
              </div>
            )}
            <Text type="secondary">共 {pendingImages.length} 张待上传</Text>
          </Space>
        )}

        <Form.Item style={{ marginTop: 16 }}>
          <Button type="primary" htmlType="submit" loading={loading}>{isEdit ? '保存' : '创建'}</Button>
        </Form.Item>
      </Form>
    </div>
  );
}
