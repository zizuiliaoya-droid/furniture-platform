import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import App from './App';
import darkTheme from './theme/antdTheme';
import './styles/global.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      theme={{
        ...darkTheme,
        algorithm: theme.darkAlgorithm,
      }}
      locale={zhCN}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>,
);
