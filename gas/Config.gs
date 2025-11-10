/**
 * 系統內部設定
 */
const GAS_CONFIG = {
  sheetId: '1i3K-MA764j2JoaVZEbgzH_eD8xWbbbOTsEpZTcJaE24',
  mainSheetName: '表單回應 1',
  settingsSheetName: '設定',
  headerRow: 1,
  dataRange: 'A1:Z1000',
  settingsRange: 'A1:Z100',
  reportFolderId: '',
  notificationEmails: ['knifewenforcursor@gmail.com'],
  defaultPeriodDays: 14,
  columnMapping: {
    timestamp: '時間戳記',
    reporter: '填表人',
    date: '日期',
    note: '特殊交接事項'
  },
  chickenColumnMapping: {
    '炸物的訂購_雞排': '雞排',
    '炸物的訂購_地瓜': '地瓜',
    '炸物的訂購_棒腿': '棒腿',
    '炸物的訂購_雞翅': '雞翅',
    '炸物的訂購_雞腿': '雞腿',
    '炸物的訂購_雞塊': '雞塊',
    '炸物的訂購_雞米花': '雞米花',
    '炸物的訂購_雞柳條': '雞柳條',
    '炸物的訂購_雞胗': '雞胗',
    '炸物的訂購_雞心': '雞心',
    '炸物的訂購_雞脖子': '雞脖子'
  },
  defaultProductConfig: {
    '雞排': { cost: 80, price: 170 },
    '地瓜': { cost: 35, price: 75 },
    '棒腿': { cost: 80, price: 170 },
    '雞翅': { cost: 105, price: 180 },
    '雞腿': { cost: 80, price: 170 },
    '雞塊': { cost: 60, price: 120 },
    '雞米花': { cost: 50, price: 100 },
    '雞柳條': { cost: 70, price: 140 },
    '雞胗': { cost: 40, price: 80 },
    '雞心': { cost: 45, price: 90 },
    '雞脖子': { cost: 30, price: 60 }
  }
};

/**
 * 允許從 Settings 工作表覆蓋品項設定。
 * 預期欄位：品項, 成本, 售價
 */
function loadProductConfig() {
  const ss = SpreadsheetApp.openById(GAS_CONFIG.sheetId);
  const sheet = ss.getSheetByName(GAS_CONFIG.settingsSheetName);
  const baseConfig = JSON.parse(JSON.stringify(GAS_CONFIG.defaultProductConfig));

  if (!sheet) {
    return baseConfig;
  }

  const values = sheet.getRange(GAS_CONFIG.settingsRange).getValues();
  const [header, ...rows] = values;
  if (!header || header.length === 0) {
    return baseConfig;
  }

  const nameIndex = header.indexOf('品項');
  const costIndex = header.indexOf('成本');
  const priceIndex = header.indexOf('售價');

  if (nameIndex === -1) {
    return baseConfig;
  }

  rows.forEach(row => {
    const name = String(row[nameIndex] || '').trim();
    if (!name) {
      return;
    }
    const cost = parseFloat(row[costIndex]) || baseConfig[name]?.cost || 0;
    const price = parseFloat(row[priceIndex]) || baseConfig[name]?.price || 0;
    baseConfig[name] = {
      cost,
      price
    };
  });

  return baseConfig;
}

/**
 * 取得提供給前端顯示的設定。
 */
function getClientConfig() {
  const now = new Date();
  const endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startDate = new Date(endDate);
  startDate.setDate(startDate.getDate() - (GAS_CONFIG.defaultPeriodDays - 1));

  return {
    sheetName: GAS_CONFIG.mainSheetName,
    defaultStartDate: formatDateForInput(startDate),
    defaultEndDate: formatDateForInput(endDate),
    products: loadProductConfig()
  };
}

function getClientConfigJson() {
  return JSON.stringify(getClientConfig());
}

function formatDateForInput(date) {
  return Utilities.formatDate(date, 'Asia/Taipei', 'yyyy-MM-dd');
}
