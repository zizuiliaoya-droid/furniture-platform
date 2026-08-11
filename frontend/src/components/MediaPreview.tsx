import { Image, Modal } from 'antd';
import DOMPurify from 'dompurify';
import { useState } from 'react';

interface MediaPreviewProps {
  filePath?: string;
  mimeType: string;
  fileName: string;
  /** 富文本内容（resource_type === 'RICH_TEXT'） */
  richTextContent?: string;
  /** 是否为富文本 */
  isRichText?: boolean;
  trigger?: React.ReactNode;
}

export function sanitizeRichText(content: string) {
  return DOMPurify.sanitize(content, { USE_PROFILES: { html: true } });
}

/**
 * 在线预览组件：图片 / PDF / 视频 / 音频 / Office / 富文本
 * 所有分支都通过 trigger 入口触发，trigger 默认是 "预览" 链接
 */
export default function MediaPreview({
  filePath, mimeType, fileName, richTextContent, isRichText, trigger,
}: MediaPreviewProps) {
  const [open, setOpen] = useState(false);
  const url = filePath ? `/media/${filePath}` : '';

  const isImage = mimeType.startsWith('image/');
  const isPdf = mimeType === 'application/pdf';
  const isVideo = mimeType.startsWith('video/');
  const isAudio = mimeType.startsWith('audio/');
  const isOffice = /\.(doc|docx|ppt|pptx|xls|xlsx)$/i.test(fileName) ||
    mimeType.includes('officedocument') || mimeType.includes('msword');

  const canPreview = isRichText || isImage || isPdf || isVideo || isAudio || isOffice;
  if (!canPreview) return null;

  const triggerNode = (
    <span onClick={() => setOpen(true)} style={{ cursor: 'pointer', display: 'inline-block' }}>
      {trigger || <a>预览</a>}
    </span>
  );

  // 图片：用 Antd Image 隐藏占位 + 受控 preview，trigger 控制 visible
  if (isImage) {
    return (
      <>
        {triggerNode}
        <Image
          src={url}
          width={0}
          height={0}
          style={{ display: 'none' }}
          preview={{ visible: open, onVisibleChange: setOpen, src: url }}
        />
      </>
    );
  }

  const renderContent = () => {
    if (isRichText) {
      const safeContent = sanitizeRichText(richTextContent || '');
      return (
        <div
          style={{ padding: '8px 0', maxHeight: '70vh', overflow: 'auto' }}
          dangerouslySetInnerHTML={{ __html: safeContent }}
        />
      );
    }
    if (isPdf) {
      return <iframe src={url} style={{ width: '100%', height: '70vh', border: 'none' }} title={fileName} />;
    }
    if (isVideo) {
      return <video src={url} controls style={{ width: '100%', maxHeight: '70vh' }} />;
    }
    if (isAudio) {
      return <audio src={url} controls style={{ width: '100%' }} />;
    }
    if (isOffice) {
      const viewerUrl = `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(window.location.origin + url)}`;
      return <iframe src={viewerUrl} style={{ width: '100%', height: '70vh', border: 'none' }} title={fileName} />;
    }
    return null;
  };

  return (
    <>
      {triggerNode}
      <Modal
        title={fileName}
        open={open}
        onCancel={() => setOpen(false)}
        footer={null}
        width="80%"
        destroyOnClose
      >
        {renderContent()}
      </Modal>
    </>
  );
}
