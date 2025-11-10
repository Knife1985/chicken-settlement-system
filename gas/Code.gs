/**
 * Web App 入口
 */
function doGet() {
  const template = HtmlService.createTemplateFromFile('Frontend');
  template.clientConfigJson = getClientConfigJson();
  return template
    .evaluate()
    .setTitle('炸雞對帳系統')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/**
 * 產生指定期間的對帳結果
 */
function generateSettlement(request) {
  const { startDate, endDate } = normalizeDateRequest(request || {});
  const report = calculateSettlementRange(startDate, endDate);
  return report;
}

/**
 * 匯出對帳報告
 */
function exportSettlementReport(request) {
  const { startDate, endDate } = normalizeDateRequest(request || {});
  const report = calculateSettlementRange(startDate, endDate);
  const file = createSettlementSpreadsheet(report);
  return {
    ok: true,
    fileUrl: file.getUrl(),
    fileId: file.getId(),
    fileName: file.getName(),
    summaryText: report.textSummary
  };
}

/**
 * 供排程呼叫
 */
function runScheduledSettlement() {
  const endDate = new Date();
  endDate.setHours(0, 0, 0, 0);
  const startDate = new Date(endDate);
  startDate.setDate(startDate.getDate() - (GAS_CONFIG.defaultPeriodDays - 1));

  const report = calculateSettlementRange(startDate, endDate);
  const file = createSettlementSpreadsheet(report);

  if (GAS_CONFIG.notificationEmails && GAS_CONFIG.notificationEmails.length) {
    const subject = `炸雞對帳報告 ${report.dateRange}`;
    const body = `${report.textSummary}\n\n報告連結：${file.getUrl()}`;
    GAS_CONFIG.notificationEmails.forEach(email => {
      try {
        GmailApp.sendEmail(email, subject, body);
      } catch (error) {
        console.error(`寄送通知失敗 (${email}): ${error}`);
      }
    });
  }

  return {
    ok: true,
    fileUrl: file.getUrl(),
    fileId: file.getId()
  };
}

/**
 * 將使用者輸入日期正規化
 */
function normalizeDateRequest(payload) {
  const end = parseInputDate(payload.endDate);
  const start = parseInputDate(payload.startDate);
  return resolveDateRange(start, end);
}

function parseInputDate(value) {
  if (!value) {
    return null;
  }
  if (value instanceof Date) {
    const clone = new Date(value.getTime());
    clone.setHours(0, 0, 0, 0);
    return clone;
  }
  if (typeof value === 'string') {
    const normalized = value.trim();
    if (!normalized) {
      return null;
    }
    const date = new Date(`${normalized}T00:00:00`);
    if (!isNaN(date.getTime())) {
      date.setHours(0, 0, 0, 0);
      return date;
    }
  }
  return null;
}

function resolveDateRange(start, end) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const endDate = end ? new Date(end.getTime()) : today;
  const startDate = start ? new Date(start.getTime()) : new Date(endDate.getTime());

  if (!start) {
    startDate.setDate(endDate.getDate() - (GAS_CONFIG.defaultPeriodDays - 1));
  }

  if (startDate > endDate) {
    const temp = new Date(startDate.getTime());
    startDate.setTime(endDate.getTime());
    endDate.setTime(temp.getTime());
  }

  startDate.setHours(0, 0, 0, 0);
  endDate.setHours(0, 0, 0, 0);

  return { startDate, endDate };
}

/**
 * 核心計算流程
 */

function normalizeSheetName(name) {
  return String(name || '')
    .replace(/[\s\u00A0\u0300-\u036F\u2000-\u200F\u3000\uFEFF]/g, '')
    .toLowerCase();
}

function resolveSheetByName(spreadsheet, expectedName) {
  const normalizedTarget = normalizeSheetName(expectedName);
  const sheets = spreadsheet.getSheets();
  for (const sheet of sheets) {
    if (normalizeSheetName(sheet.getName()) === normalizedTarget) {
      return sheet;
    }
  }
  const available = sheets.map(sheet => sheet.getName()).join(', ');
  throw new Error(`找不到工作表：${expectedName}（現有分頁：${available}）`);
}

function calculateSettlementRange(startDate, endDate) {
  const productConfig = loadProductConfig();
  const dataBundle = fetchSalesRecords(startDate, endDate, productConfig);
  const report = buildSettlementReport(dataBundle, productConfig, startDate, endDate);
  return report;
}

function fetchSalesRecords(startDate, endDate, productConfig) {
  const ss = SpreadsheetApp.openById(GAS_CONFIG.sheetId);
  const sheet = resolveSheetByName(ss, GAS_CONFIG.mainSheetName);

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  const displayData = dataRange.getDisplayValues();
  if (!data || data.length <= GAS_CONFIG.headerRow) {
    const headers = displayData && displayData.length ? displayData[0] : [];
    return { records: [], rawRows: [], headers };
  }

  const headers = displayData[GAS_CONFIG.headerRow - 1].map(value => String(value || '').trim());
  const headerIndex = {};
  headers.forEach((name, index) => {
    headerIndex[name] = index;
  });

  const dateHeader = GAS_CONFIG.columnMapping.date;
  const timestampHeader = GAS_CONFIG.columnMapping.timestamp;
  const reporterHeader = GAS_CONFIG.columnMapping.reporter;
  const noteHeader = GAS_CONFIG.columnMapping.note;

  const dateColumnIndex = headerIndex[dateHeader];
  if (dateColumnIndex === undefined) {
    throw new Error(`資料列缺少「${dateHeader}」欄位`);
  }

  const timestampIndex = timestampHeader ? headerIndex[timestampHeader] : undefined;
  const reporterIndex = reporterHeader ? headerIndex[reporterHeader] : undefined;
  const noteIndex = noteHeader ? headerIndex[noteHeader] : undefined;

  const records = [];
  const rawRows = [];
  const latestRowIndexByDate = {};

  const startParts = convertDateToParts(startDate);
  const endParts = convertDateToParts(endDate);
  const startNumeric = datePartsToNumber(startParts);
  const endNumeric = datePartsToNumber(endParts);

  for (let i = GAS_CONFIG.headerRow; i < data.length; i++) {
    const row = data[i];
    const displayRow = displayData[i];
    if (!row || row.every(value => value === '' || value === null)) {
      continue;
    }

    const dateValue = row[dateColumnIndex];
    const dateDisplay = displayRow[dateColumnIndex];
    const dateObj = parseSheetDate(dateValue, dateDisplay);
    if (!dateObj) {
      continue;
    }

    const dateParts = parseDateParts(dateValue, dateDisplay);
    if (!dateParts) {
      continue;
    }
    const dateNumeric = datePartsToNumber(dateParts);
    if (dateNumeric < startNumeric || dateNumeric > endNumeric) {
      continue;
    }

    const dateKey = datePartsToKey(dateParts);
    const timestampDisplay = timestampIndex !== undefined ? displayRow[timestampIndex] : null;
    const timestampValue = timestampIndex !== undefined ? parseSheetDateTime(row[timestampIndex], timestampDisplay) : null;
    const timestampMillis = timestampValue ? timestampValue.getTime() : null;

    const existing = latestRowIndexByDate[dateKey];
    if (!existing) {
      latestRowIndexByDate[dateKey] = { index: i, timestamp: timestampMillis ?? i };
    } else {
      const candidateTimestamp = timestampMillis ?? i;
      if (candidateTimestamp > existing.timestamp || (candidateTimestamp === existing.timestamp && i > existing.index)) {
        latestRowIndexByDate[dateKey] = { index: i, timestamp: candidateTimestamp };
      }
    }
  }

  for (let i = GAS_CONFIG.headerRow; i < data.length; i++) {
    const row = data[i];
    const displayRow = displayData[i];
    if (!row || row.every(value => value === '' || value === null)) {
      continue;
    }

    const dateValue = row[dateColumnIndex];
    const dateDisplay = displayRow[dateColumnIndex];
    const dateObj = parseSheetDate(dateValue, dateDisplay);
    if (!dateObj) {
      continue;
    }

    const dateParts = parseDateParts(dateValue, dateDisplay);
    if (!dateParts) {
      continue;
    }
    const dateNumeric = datePartsToNumber(dateParts);
    if (dateNumeric < startNumeric || dateNumeric > endNumeric) {
      continue;
    }

    const dateStr = datePartsToKey(dateParts);
    const latestInfo = latestRowIndexByDate[dateStr];
    if (!latestInfo || latestInfo.index !== i) {
      continue;
    }

    const reporter = reporterIndex !== undefined ? row[reporterIndex] || '' : '';
    const note = noteIndex !== undefined ? row[noteIndex] || '' : '';

    rawRows.push({
      rowNumber: i + 1,
      date: dateStr,
      reporter,
      note
    });

    Object.entries(GAS_CONFIG.chickenColumnMapping).forEach(([columnName, itemName]) => {
      const columnIndex = headerIndex[columnName];
      if (columnIndex === undefined) {
        return;
      }

      const quantity = parseNumber(row[columnIndex]);
      if (quantity <= 0) {
        return;
      }

      const itemConfig = productConfig[itemName] || { cost: 0, price: 0 };
      const unitCost = itemConfig.cost || 0;
      const unitPrice = itemConfig.price || 0;

      records.push({
        date: dateStr,
        item: itemName,
        quantity,
        unitCost,
        unitPrice,
        costTotal: quantity * unitCost,
        salesTotal: quantity * unitPrice,
        reporter,
        note
      });
    });
  }

  return { records, rawRows, headers };
}

function padNumber(value) {
  return String(value).padStart(2, '0');
}

function datePartsToKey(parts) {
  return `${parts.year}-${padNumber(parts.month)}-${padNumber(parts.day)}`;
}

function datePartsToNumber(parts) {
  return parts.year * 10000 + parts.month * 100 + parts.day;
}

function convertDateToParts(date) {
  return {
    year: date.getFullYear(),
    month: date.getMonth() + 1,
    day: date.getDate()
  };
}

function parseDateParts(value, displayValue) {
  const fromDisplay = parseDateFromString(displayValue);
  if (fromDisplay) {
    return {
      year: fromDisplay.getFullYear(),
      month: fromDisplay.getMonth() + 1,
      day: fromDisplay.getDate()
    };
  }

  if (value instanceof Date) {
    const year = value.getFullYear();
    const month = value.getMonth() + 1;
    const day = value.getDate();
    if (year && month && day) {
      return { year, month, day };
    }
  }

  if (typeof value === 'number') {
    const epoch = new Date(1899, 11, 30);
    const millis = Math.round(value * 24 * 60 * 60 * 1000);
    const date = new Date(epoch.getTime() + millis);
    return {
      year: date.getFullYear(),
      month: date.getMonth() + 1,
      day: date.getDate()
    };
  }

  const fromValue = parseDateFromString(value);
  if (fromValue) {
    return {
      year: fromValue.getFullYear(),
      month: fromValue.getMonth() + 1,
      day: fromValue.getDate()
    };
  }

  return null;
}

function parseDateFromString(value) {
  if (!value) {
    return null;
  }
  const trimmed = String(value).trim();
  if (!trimmed) {
    return null;
  }
  const normalized = trimmed
    .replace(/[年\.\-]/g, '/')
    .replace(/[月]/g, '/')
    .replace(/[日]/g, '')
    .replace(/\s+/g, '/');
  const match = normalized.match(/(\d{4})\D?(\d{1,2})\D?(\d{1,2})/);
  if (!match) {
    return null;
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  if (!year || !month || !day) {
    return null;
  }
  const date = new Date(year, month - 1, day);
  date.setHours(0, 0, 0, 0);
  return date;
}

function parseSheetDateTime(value, displayValue) {
  if (!value && value !== 0) {
    value = displayValue;
  }
  if (value instanceof Date) {
    return new Date(value.getTime());
  }
  if (typeof value === 'number') {
    const epoch = new Date(1899, 11, 30);
    const millis = Math.round(value * 24 * 60 * 60 * 1000);
    return new Date(epoch.getTime() + millis);
  }
  if (value) {
    const parsed = new Date(String(value).trim());
    if (!isNaN(parsed.getTime())) {
      return parsed;
    }
  }
  return null;
}

function parseSheetDate(value, displayValue) {
  if (value instanceof Date) {
    const date = new Date(value.getTime());
    date.setHours(0, 0, 0, 0);
    return date;
  }
  if (typeof value === 'number') {
    const epoch = new Date(1899, 11, 30);
    const date = new Date(epoch.getTime() + value * 24 * 60 * 60 * 1000);
    date.setHours(0, 0, 0, 0);
    return date;
  }
  const fromString = parseDateFromString(value) || parseDateFromString(displayValue);
  if (fromString) {
    return fromString;
  }
  return null;
}

function buildSettlementReport(dataBundle, productConfig, startDate, endDate) {
  const byItem = {};
  const byDate = {};
  let totalQuantity = 0;
  let totalSales = 0;
  let totalRevenue = 0;

  dataBundle.records.forEach(record => {
    totalQuantity += record.quantity;
    totalSales += record.salesTotal;
    totalRevenue += record.costTotal;

    if (!byItem[record.item]) {
      byItem[record.item] = {
        name: record.item,
        quantity: 0,
        costPrice: record.unitCost,
        costTotal: 0,
        unitPrice: record.unitPrice,
        salesTotal: 0
      };
    }

    const itemAgg = byItem[record.item];
    itemAgg.quantity += record.quantity;
    itemAgg.costTotal += record.costTotal;
    itemAgg.salesTotal += record.salesTotal;
    if (record.unitCost) {
      itemAgg.costPrice = record.unitCost;
    }
    if (record.unitPrice) {
      itemAgg.unitPrice = record.unitPrice;
    }

    if (!byDate[record.date]) {
      byDate[record.date] = {
        date: record.date,
        totalQuantity: 0,
        totalCost: 0,
        totalSales: 0,
        items: {}
      };
    }

    const dayAgg = byDate[record.date];
    dayAgg.totalQuantity += record.quantity;
    dayAgg.totalCost += record.costTotal;
    dayAgg.totalSales += record.salesTotal;

    if (!dayAgg.items[record.item]) {
      dayAgg.items[record.item] = {
        name: record.item,
        quantity: 0,
        costPrice: record.unitCost,
        costTotal: 0,
        unitPrice: record.unitPrice,
        salesTotal: 0
      };
    }

    const dayItem = dayAgg.items[record.item];
    dayItem.quantity += record.quantity;
    dayItem.costTotal += record.costTotal;
    dayItem.salesTotal += record.salesTotal;
  });

  const categories = Object.values(byItem).sort((a, b) => a.name.localeCompare(b.name, 'zh-TW'));
  const dailyDetails = Object.values(byDate)
    .sort((a, b) => a.date.localeCompare(b.date))
    .map(day => ({
      date: day.date,
      totalQuantity: day.totalQuantity,
      totalCost: day.totalCost,
      totalSales: day.totalSales,
      items: Object.values(day.items).sort((a, b) => a.name.localeCompare(b.name, 'zh-TW'))
    }));

  const report = {
    startDate: formatDateForDisplay(startDate),
    endDate: formatDateForDisplay(endDate),
    dateRange: `${formatDateForDisplay(startDate)} 至 ${formatDateForDisplay(endDate)}`,
    totalQuantity,
    totalSales,
    totalRevenue,
    revenueRatio: totalSales > 0 ? totalRevenue / totalSales : 0,
    profit: totalSales - totalRevenue,
    categories,
    dailyDetails,
    products: productConfig,
    rawRecords: dataBundle.records,
    rawRows: dataBundle.rawRows,
    headers: dataBundle.headers
  };

  report.textSummary = buildTextSummary(report);
  return report;
}

function buildTextSummary(report) {
  if (!report.dailyDetails.length) {
    return `期間：${report.dateRange}\n無炸雞銷售資料`;
  }

  const lines = [];
  lines.push('='.repeat(50));
  lines.push('🍗 炸雞對帳摘要');
  lines.push('='.repeat(50));
  lines.push(`對帳期間：${report.dateRange}`);
  lines.push('');
  lines.push('📅 每日明細：');
  lines.push('-'.repeat(30));

  report.dailyDetails.forEach(day => {
    lines.push(`📅 ${day.date}：`);
    day.items.forEach(item => {
      lines.push(`  ${item.name}：${formatNumber(item.quantity, 0)} 份 × ${formatNumber(item.costPrice, 0)} 元（進價） = ${formatCurrency(item.costTotal)} 元`);
    });
    lines.push('');
  });

  lines.push('📊 每日總計（進價）：');
  report.dailyDetails.forEach(day => {
    lines.push(`${day.date}：總計 ${formatNumber(day.totalQuantity, 0)} 份，進價 ${formatCurrency(day.totalCost)} 元`);
  });
  lines.push('');

  lines.push('🍗 品項對帳明細：');
  lines.push('-'.repeat(30));
  report.categories.forEach(item => {
    lines.push(`${item.name}：${formatNumber(item.quantity, 0)} 份 × ${formatNumber(item.costPrice, 0)} 元（進價） = ${formatCurrency(item.costTotal)} 元`);
  });
  lines.push('');

  lines.push('🧮 計算式：');
  lines.push('-'.repeat(30));
  lines.push(`總數量：${formatNumber(report.totalQuantity, 0)} 份`);
  lines.push(`應付金額：${formatCurrency(report.totalRevenue)} 元`);
  lines.push('');
  lines.push('金額計算明細：');
  report.categories.forEach(item => {
    lines.push(`  ${item.name}：${formatNumber(item.quantity, 0)} 份 × ${formatNumber(item.costPrice, 0)} 元 = ${formatCurrency(item.costTotal)} 元`);
  });
  lines.push('');
  lines.push('='.repeat(50));
  lines.push(`💰 應付金額：${formatCurrency(report.totalRevenue)} 元`);
  lines.push('='.repeat(50));

  return lines.join('\n');
}

function formatDateForDisplay(date) {
  return Utilities.formatDate(date, 'Asia/Taipei', 'yyyy-MM-dd');
}

function formatCurrency(value) {
  return `${formatNumber(value, 0)}`;
}

function formatNumber(value, decimals) {
  const number = Number(value || 0);
  return number.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

function parseNumber(value) {
  if (typeof value === 'number') {
    return value;
  }
  if (typeof value === 'string') {
    const cleaned = value.replace(/[^\d\-\.]/g, '');
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? 0 : parsed;
  }
  return 0;
}

function createSettlementSpreadsheet(report) {
  const timestamp = Utilities.formatDate(new Date(), 'Asia/Taipei', 'yyyyMMdd_HHmmss');
  const name = `炸雞對帳報告_${timestamp}`;
  const ss = SpreadsheetApp.create(name);
  const summarySheet = ss.getActiveSheet();
  summarySheet.setName('結算摘要');

  summarySheet.getRange(1, 1, 6, 2).setValues([
    ['項目', '內容'],
    ['對帳期間', report.dateRange],
    ['總銷售額', formatCurrency(report.totalSales)],
    ['炸雞老闆應付', formatCurrency(report.totalRevenue)],
    ['利潤', formatCurrency(report.profit)],
    ['成本比例', `${(report.revenueRatio * 100).toFixed(1)}%`]
  ]);
  summarySheet.autoResizeColumns(1, 2);

  const productSheet = ss.insertSheet('品項摘要');
  productSheet.getRange(1, 1, 1, 6).setValues([
    ['品項', '數量', '單位成本', '成本總額', '單位售價', '銷售總額']
  ]);
  const productRows = report.categories.map(item => [
    item.name,
    item.quantity,
    item.costPrice,
    item.costTotal,
    item.unitPrice,
    item.salesTotal
  ]);
  if (productRows.length) {
    productSheet.getRange(2, 1, productRows.length, 6).setValues(productRows);
  }
  productSheet.autoResizeColumns(1, 6);

  const dailySheet = ss.insertSheet('每日摘要');
  dailySheet.getRange(1, 1, 1, 4).setValues([
    ['日期', '總數量', '進價總額', '銷售總額']
  ]);
  const dailyRows = report.dailyDetails.map(day => [
    day.date,
    day.totalQuantity,
    day.totalCost,
    day.totalSales
  ]);
  if (dailyRows.length) {
    dailySheet.getRange(2, 1, dailyRows.length, 4).setValues(dailyRows);
  }
  dailySheet.autoResizeColumns(1, 4);

  const detailSheet = ss.insertSheet('明細資料');
  detailSheet.getRange(1, 1, 1, 7).setValues([
    ['日期', '品項', '數量', '單位成本', '成本總額', '單位售價', '銷售總額']
  ]);
  const detailRows = report.rawRecords.map(record => [
    record.date,
    record.item,
    record.quantity,
    record.unitCost,
    record.costTotal,
    record.unitPrice,
    record.salesTotal
  ]);
  if (detailRows.length) {
    detailSheet.getRange(2, 1, detailRows.length, 7).setValues(detailRows);
  }
  detailSheet.autoResizeColumns(1, 7);

  const textSheet = ss.insertSheet('文字摘要');
  const textLines = report.textSummary.split('\n');
  textLines.forEach((line, index) => {
    textSheet.getRange(index + 1, 1).setValue(line);
  });
  textSheet.autoResizeColumn(1);

  // 移除自動建立的空白 Sheet（如果存在）
  const sheets = ss.getSheets();
  if (sheets.length > 5) {
    const lastSheet = sheets[sheets.length - 1];
    if (lastSheet.getName() === 'Sheet1') {
      ss.deleteSheet(lastSheet);
    }
  }

  const file = DriveApp.getFileById(ss.getId());
  if (GAS_CONFIG.reportFolderId) {
    try {
      const folder = DriveApp.getFolderById(GAS_CONFIG.reportFolderId);
      folder.addFile(file);
      const root = DriveApp.getRootFolder();
      root.removeFile(file);
    } catch (error) {
      console.warn(`無法移動檔案到指定資料夾：${error}`);
    }
  }

  return file;
}
