/**
 * 智楷家具 – Dark-mode Ant Design theme.
 *
 * Design principles (from spec):
 *  - NO pure black (#000) backgrounds; use deep blue-grey tones
 *  - Text opacity layers: 87% emphasis, 60% body, 38% hint
 *  - De-saturated, lifted-lightness palette to avoid optical vibration
 *  - Filled/bold icons preferred over thin strokes
 *  - Soft shadows; use brightness layers instead of hard drop-shadows
 */
import type { ThemeConfig } from 'antd';

const darkTheme: ThemeConfig = {
  token: {
    /* ---- Brand ---- */
    colorPrimary: '#6b8acd',          // de-saturated blue
    colorSuccess: '#6dae82',          // soft green
    colorWarning: '#d4a44a',          // muted gold
    colorError: '#cf6b6b',            // soft red
    colorInfo: '#5fa8d3',             // calm blue

    /* ---- Backgrounds ---- */
    colorBgContainer: '#1e2433',      // card / container surface
    colorBgLayout: '#161b26',         // page background
    colorBgElevated: '#252b3b',       // dropdown / popover
    colorBgSpotlight: '#2a3245',      // hover highlight

    /* ---- Text (white with opacity layers) ---- */
    colorText: 'rgba(255,255,255,0.87)',          // emphasis
    colorTextSecondary: 'rgba(255,255,255,0.60)', // body
    colorTextTertiary: 'rgba(255,255,255,0.38)',  // hint
    colorTextQuaternary: 'rgba(255,255,255,0.18)',

    /* ---- Borders ---- */
    colorBorder: 'rgba(255,255,255,0.12)',
    colorBorderSecondary: 'rgba(255,255,255,0.08)',

    /* ---- Misc ---- */
    borderRadius: 6,
    fontFamily: "'DM Sans', 'Inter', 'Noto Sans SC', -apple-system, sans-serif",
    fontSize: 14,
    boxShadow: '0 2px 12px rgba(0,0,0,0.28)',
    boxShadowSecondary: '0 4px 20px rgba(0,0,0,0.35)',
  },

  components: {
    Layout: {
      siderBg: '#1a2030',
      headerBg: '#1e2433',
      bodyBg: '#161b26',
    },
    Menu: {
      darkItemBg: '#1a2030',
      darkItemSelectedBg: '#2a3245',
      darkItemHoverBg: '#252b3b',
      itemBorderRadius: 6,
    },
    Card: {
      colorBgContainer: '#1e2433',
      borderRadiusLG: 8,
    },
    Table: {
      colorBgContainer: '#1e2433',
      headerBg: '#252b3b',
      rowHoverBg: '#252b3b',
      borderRadius: 8,
    },
    Button: {
      borderRadius: 6,
      controlHeight: 38,
    },
    Input: {
      colorBgContainer: '#252b3b',
      borderRadius: 6,
      controlHeight: 38,
      activeBorderColor: '#6b8acd',
      hoverBorderColor: '#5a7ab8',
    },
    Select: {
      colorBgContainer: '#252b3b',
      optionSelectedBg: '#2a3245',
    },
    Modal: {
      contentBg: '#1e2433',
      headerBg: '#1e2433',
    },
    Descriptions: {
      colorTextLabel: 'rgba(255,255,255,0.60)',
    },
    Statistic: {
      contentFontSize: 28,
    },
    Tag: {
      borderRadiusSM: 4,
    },
    Tree: {
      colorBgContainer: 'transparent',
    },
  },
};

export default darkTheme;
