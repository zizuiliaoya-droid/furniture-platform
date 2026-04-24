/**
 * Dark-theme login page with interactive desk-lamp SVG.
 *
 * Lamp interaction:
 *  - GSAP Draggable pull-cord; drag > 50 px toggles on/off
 *  - Elastic cord snap-back animation
 *  - "Click" sound effect on toggle
 *  - Random hue each time the lamp turns on
 *  - Eyes rotate 180° when off, 0° when on
 *
 * Login form:
 *  - Hidden (opacity 0, scale 0.8) when lamp is off
 *  - Spring cubic-bezier entrance when lamp turns on
 *  - Border / shadow colour follows lamp hue
 *  - Inputs glow on focus
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { Button, Form, Input, message, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import gsap from 'gsap';
import { Draggable } from 'gsap/Draggable';
import './LoginPage.css';

gsap.registerPlugin(Draggable);

const { Title, Text } = Typography;

/* ------------------------------------------------------------------ */
/*  Tiny inline "click" sound – base-64 encoded so no extra assets    */
/* ------------------------------------------------------------------ */
const CLICK_SOUND_B64 =
  'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=';

function playClick() {
  try {
    const a = new Audio(CLICK_SOUND_B64);
    a.volume = 0.35;
    a.play().catch(() => {});
  } catch {
    /* silent fallback */
  }
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */
export default function LoginPage() {
  const [lampOn, setLampOn] = useState(false);
  const [hue, setHue] = useState(200);
  const [loading, setLoading] = useState(false);

  const cordHandleRef = useRef<SVGCircleElement>(null);
  const cordLineRef = useRef<SVGPathElement>(null);
  const cordKnobRef = useRef<SVGCircleElement>(null);
  const draggableInstance = useRef<Draggable[]>();

  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  /* ---- toggle helper (stable ref so GSAP closure stays fresh) ---- */
  const lampOnRef = useRef(lampOn);
  lampOnRef.current = lampOn;

  const toggleLamp = useCallback(() => {
    const next = !lampOnRef.current;
    if (next) setHue(Math.floor(Math.random() * 360));
    setLampOn(next);
    playClick();
  }, []);

  /* ---- GSAP Draggable for pull-cord ---- */
  useEffect(() => {
    if (!cordHandleRef.current) return;

    draggableInstance.current = Draggable.create(cordHandleRef.current, {
      type: 'y',
      bounds: { minY: 0, maxY: 80 },
      onDragStart() {
        /* Kill any in-flight snap-back animations so position is clean */
        gsap.killTweensOf(cordHandleRef.current);
        gsap.killTweensOf(cordLineRef.current);
        gsap.killTweensOf(cordKnobRef.current);
        /* Reset to 0 so this.y is a reliable offset */
        gsap.set(cordHandleRef.current, { y: 0 });
        if (cordLineRef.current) {
          cordLineRef.current.setAttribute('d', 'M130,110 Q130,142 130,175');
        }
        if (cordKnobRef.current) {
          cordKnobRef.current.setAttribute('cy', '183');
        }
      },
      onDrag() {
        const dy = this.y;
        /* Update cord path in real-time to follow the handle */
        if (cordLineRef.current) {
          cordLineRef.current.setAttribute(
            'd',
            `M130,110 Q${130 + dy * 0.15},${142 + dy * 0.5} 130,${175 + dy}`,
          );
        }
        /* Move the knob with the handle */
        if (cordKnobRef.current) {
          cordKnobRef.current.setAttribute('cy', String(183 + dy));
        }
      },
      onDragEnd() {
        /* this.y is the total downward offset from rest position */
        const pulled = this.y;

        /* Elastic cord snap-back (handle) */
        gsap.to(cordHandleRef.current, {
          y: 0,
          duration: 0.5,
          ease: 'elastic.out(1.2, 0.35)',
        });

        /* Animate the cord path back to rest */
        if (cordLineRef.current) {
          gsap.to(cordLineRef.current, {
            attr: { d: 'M130,110 Q130,142 130,175' },
            duration: 0.6,
            ease: 'elastic.out(1, 0.3)',
          });
        }

        /* Animate the knob back to rest */
        if (cordKnobRef.current) {
          gsap.to(cordKnobRef.current, {
            attr: { cy: 183 },
            duration: 0.5,
            ease: 'elastic.out(1.2, 0.35)',
          });
        }

        if (pulled > 50) toggleLamp();
      },
    });

    return () => {
      draggableInstance.current?.forEach((d) => d.kill());
    };
  }, [toggleLamp]);

  /* ---- Login handler ---- */
  const handleLogin = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      message.success('登录成功');
      navigate('/');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  /* ---- Derived colours ---- */
  const lampColor = `hsl(${hue}, 70%, 60%)`;
  const glowColor = `hsl(${hue}, 70%, 40%)`;

  return (
    <div
      className="login-page"
      style={
        {
          '--on': lampOn ? 1 : 0,
          '--shade-hue': hue,
          '--lamp-color': lampColor,
          '--glow-color': glowColor,
        } as React.CSSProperties
      }
    >
      {/* ==================== Desk Lamp SVG ==================== */}
      <svg
        width="220"
        height="320"
        viewBox="0 0 220 320"
        className="lamp-svg"
      >
        {/* Light cone (visible when on) */}
        {lampOn && (
          <ellipse cx="110" cy="180" rx="70" ry="100" fill={lampColor} opacity="0.08" />
        )}
        {lampOn && (
          <ellipse cx="110" cy="160" rx="45" ry="70" fill={lampColor} opacity="0.12" />
        )}

        {/* Base */}
        <ellipse cx="110" cy="295" rx="65" ry="14" fill="#2a2a3a" />
        <rect x="100" y="282" width="20" height="14" rx="2" fill="#2a2a3a" />

        {/* Pole */}
        <rect x="106" y="130" width="8" height="155" fill="#3a3a4a" rx="4" />

        {/* Shade */}
        <path
          d="M55 130 L110 85 L165 130 Z"
          fill="#3a3a4a"
          stroke={lampOn ? lampColor : '#555'}
          strokeWidth="2"
        />

        {/* Bulb */}
        <circle
          cx="110"
          cy="125"
          r="10"
          fill={lampOn ? lampColor : '#444'}
          style={{
            filter: lampOn ? `drop-shadow(0 0 12px ${lampColor})` : 'none',
            transition: 'fill 0.4s, filter 0.4s',
          }}
        />

        {/* Eyes */}
        <g
          style={{
            transform: `translate(110px, 108px) rotate(${lampOn ? 0 : 180}deg)`,
            transformOrigin: '0 0',
            transition: 'transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
          }}
        >
          <circle cx="-12" cy="0" r="5" fill={lampOn ? '#fff' : '#555'} />
          <circle cx="12" cy="0" r="5" fill={lampOn ? '#fff' : '#555'} />
          <circle cx="-12" cy="-1.5" r="2" fill={lampOn ? '#222' : '#444'} />
          <circle cx="12" cy="-1.5" r="2" fill={lampOn ? '#222' : '#444'} />
        </g>

        {/* Pull cord (path for morph animation) */}
        <path
          ref={cordLineRef}
          d="M130,110 Q130,142 130,175"
          stroke="#888"
          strokeWidth="1.5"
          fill="none"
        />
        {/* Cord handle (draggable) */}
        <circle
          ref={cordHandleRef}
          cx="130"
          cy="175"
          r="7"
          fill="#aaa"
          stroke="#999"
          strokeWidth="1"
          style={{ cursor: 'grab' }}
        />
        {/* Small knob at end of cord */}
        <circle ref={cordKnobRef} cx="130" cy="183" r="3" fill="#999" style={{ pointerEvents: 'none' }} />
      </svg>

      {/* ==================== Login Form ==================== */}
      <div
        className="login-card"
        style={{
          opacity: lampOn ? 1 : 0,
          transform: lampOn ? 'scale(1)' : 'scale(0.8)',
          borderColor: lampOn ? lampColor : 'transparent',
          boxShadow: lampOn ? `0 0 60px ${glowColor}30, 0 0 20px ${glowColor}18` : 'none',
          pointerEvents: lampOn ? 'auto' : 'none',
        }}
      >
        <Title level={3} style={{ color: '#fff', textAlign: 'center', marginBottom: 32 }}>
          欢迎回来
        </Title>

        <Form onFinish={handleLogin} size="large" autoComplete="off">
          <Form.Item name="username" rules={[{ required: true, message: '请输入账号' }]}>
            <Input
              prefix={<UserOutlined style={{ color: '#666' }} />}
              placeholder="账号"
              className="login-input"
              style={{ '--focus-color': lampColor, '--focus-glow': glowColor } as React.CSSProperties}
            />
          </Form.Item>

          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password
              prefix={<LockOutlined style={{ color: '#666' }} />}
              placeholder="密码"
              className="login-input"
              style={{ '--focus-color': lampColor, '--focus-glow': glowColor } as React.CSSProperties}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={loading}
              className="login-btn"
              style={{ background: lampColor, borderColor: lampColor }}
            >
              登录
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Text
              className="forgot-link"
              onClick={() => message.info('请联系管理员重置密码')}
            >
              忘记密码？
            </Text>
          </div>
        </Form>
      </div>
    </div>
  );
}
