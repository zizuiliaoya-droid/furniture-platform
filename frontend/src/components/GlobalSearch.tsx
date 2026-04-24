import { useState } from 'react';
import { Input, Dropdown, Typography, Space, Empty } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { searchService } from '../services/searchService';

const { Text } = Typography;

export default function GlobalSearch() {
  const [results, setResults] = useState<any>(null);
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (value: string) => {
    if (value.length < 2) { setResults(null); setOpen(false); return; }
    const { data } = await searchService.search(value);
    setResults(data);
    setOpen(true);
  };

  const items = results ? [
    ...((results.products || []).map((p: any) => ({
      key: `p-${p.id}`, label: <Space><Text type="secondary">[产品]</Text>{p.name}</Space>,
      onClick: () => { navigate(`/products/${p.id}`); setOpen(false); },
    }))),
    ...((results.cases || []).map((c: any) => ({
      key: `c-${c.id}`, label: <Space><Text type="secondary">[案例]</Text>{c.title}</Space>,
      onClick: () => { navigate(`/cases/${c.id}`); setOpen(false); },
    }))),
    ...((results.documents || []).map((d: any) => ({
      key: `d-${d.id}`, label: <Space><Text type="secondary">[文档]</Text>{d.name}</Space>,
    }))),
    ...((results.quotes || []).map((q: any) => ({
      key: `q-${q.id}`, label: <Space><Text type="secondary">[报价]</Text>{q.title}</Space>,
      onClick: () => { navigate(`/quotes/${q.id}`); setOpen(false); },
    }))),
  ] : [];

  return (
    <Dropdown menu={{ items: items.length ? items : [{ key: 'empty', label: <Empty description="无结果" /> }] }} open={open && !!results} onOpenChange={setOpen}>
      <Input prefix={<SearchOutlined />} placeholder="搜索产品、案例、文档、报价..." allowClear
        onChange={(e) => handleSearch(e.target.value)} style={{ width: 300 }} />
    </Dropdown>
  );
}
