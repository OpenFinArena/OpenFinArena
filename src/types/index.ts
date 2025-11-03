/**
 * 市场代码与国旗图片的映射表
 * key: 市场代码（与 MarketCode 类型对应）
 * value: 国旗图片路径（建议使用相对路径或CDN链接）
 */
export const flagMap = {
  US: '/images/flag/us.svg', // 美国
  UK: '/images/flag/uk.svg', // 英国
  CN: '/images/flag/cn.svg', // 中国
  HK: '/images/flag/hk.svg', // 中国香港
  SG: '/images/flag/sg.svg', // 新加坡
  AU: '/images/flag/au.svg', // 澳大利亚
  MY: '/images/flag/my.svg', // 马来西亚
  ID: '/images/flag/id.svg', // 印度尼西亚
}
export const countryList = [
  {
    label: 'US',
    value: 'us',
    src: '/images/flag/us.svg',
  },
  {
    label: 'UK',
    value: 'uk',
    src: '/images/flag/uk.svg',
  },
  {
    label: 'CN',
    value: 'cn',
    src: '/images/flag/cn.svg',
  },
  {
    label: 'HK',
    value: 'hk',
    src: '/images/flag/hk.svg',
  },
  {
    label: 'SG',
    value: 'sg',
    src: '/images/flag/sg.svg',
  },
  {
    label: 'AU',
    value: 'au',
    src: '/images/flag/au.svg',
  },
  {
    label: 'MY',
    value: 'my',
    src: '/images/flag/my.svg',
  },
  {
    label: 'ID',
    value: 'ind',
    src: '/images/flag/id.svg',
  },
]

// 国家/地区代码枚举
// export type MarketCode = 'US' | 'UK' | 'CN' | 'HK' | 'SG' | 'AU' | 'MY' | 'ID'
// 导出市场代码类型（与之前的 MarketCode 保持一致）
export type MarketCode = keyof typeof flagMap

// 单条数据接口
export interface CompanyItem {
  market: MarketCode
  companyName: string
  inputFiles: string[]
  inputStructure: string
  referenceReportWord: string
  referenceReportMarkdown: string
}

// 表格数据集类型
export type CompanyTableData = CompanyItem[]
