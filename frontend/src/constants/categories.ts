// 产品分类中文标签映射（与后端 CategoryOptionsService 保持一致，用于展示）

export const L1_LABELS: Record<string, string> = {
  SEATING: '坐具类',
  DESKS_WORKSTATIONS: '工位办公桌类',
  TABLE: '桌台类',
  STORAGE: '收纳储物类',
  ACCESSORIES: '配套附件类',
  EDUCATION: '教育家具类',
};

export const L2_LABELS: Record<string, string> = {
  // 坐具类
  OFFICE_CHAIR: '办公椅',
  GUEST_CHAIR: '访客椅',
  CONFERENCE_CHAIR: '会议椅',
  STOOL: '凳子',
  LOUNGE_SEATING: '休闲坐具',
  VISITOR_SEATING: '接待椅',
  OPERATOR_SEATING: '职员椅',
  // 工位办公桌类
  DESK: '办公桌',
  HEIGHT_ADJUSTABLE_DESK: '升降桌',
  BENCHING: '屏风工位',
  PRIVATE_OFFICE: '独立办公室办公桌',
  // 桌台类
  CONFERENCE_TABLE: '会议/协作桌',
  OCCASIONAL_TABLE: '休闲桌',
  OUTDOOR_TABLE: '户外桌及遮阳设施',
  // 收纳储物类
  WORKSTATION_STORAGE: '工位收纳',
  LOCKER: '储物柜',
  CABINET_CREDENZA: '文件柜/矮柜',
  BOOKCASE_SHELVING: '书柜/置物架',
  CART: '移动推车',
  // 配套附件类
  MODULAR_WALL: '模块化隔断及隔音材料',
  POD: '独立 Pod 单元',
  FREESTANDING_SCREEN: '独立屏风',
  SPACE_DIVISION: '建筑/空间分割件',
  MONITOR_ARM: '显示器支架及配件',
  CABLE_MANAGEMENT: '电源/线缆管理',
  LIGHTING: '照明设备',
  ACC_TABLE: '附属桌台配件',
  // 教育家具类
  CLASSROOM_CHAIR: '教室椅',
  EDUCATION_LOUNGE: '教育休闲家具',
  EDU_SEATING: '教育类坐具',
  CLASSROOM_STORAGE: '教室收纳',
  EDU_DESK: '教育类工位桌',
  EDU_ACCESSORY: '教育类附件',
};

export const l1Label = (code: string) => L1_LABELS[code] || code || '-';
export const l2Label = (code: string) => L2_LABELS[code] || code || '-';
