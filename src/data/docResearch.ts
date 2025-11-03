interface SampleData {
  market: string
  companyName: string
  inputAnnualReports: string[]
  sampleOutputReport: string
}

interface Dataset {
  market: string
  companyCount: number
  documentCount: number
  maxPageCount: number,
  minPageCount: number,
  avgPageCount: number,
  examples: string[]
}

export interface ScoreItem {
  method: string
  organization: string
  score: number
  team: string
  submittedDate: string
  us: number
  uk: number
  cn: number
  hk: number
  sg: number
  au: number
  ind: number
  my: number
  model?: string
  imageType?: string
}


export const samplesData: SampleData[] = [
  {
    market: 'US',
    companyName: 'Nvidia',
    inputAnnualReports: ['NVIDIA_2024.pdf', 'NVIDIA_2023.pdf'],
    sampleOutputReport: 'sample001.md',
  },
  {
    market: 'UK',
    companyName: 'Chenming Group PLC',
    inputAnnualReports: ['Chenming Group_2024.pdf', 'Chenming Group_2023.pdf'],
    sampleOutputReport: 'sample002.md',
  },
  {
    market: 'CN',
    companyName: '宁德时代新能源科技股份有限公司',
    inputAnnualReports: [
      '宁德时代新能源科技股份有限公司_2024.pdf',
      '宁德时代新能源科技股份有限公司_2023.pdf',
    ],
    sampleOutputReport: 'sample003.md',
  },
  {
    market: 'HK',
    companyName: '腾讯',
    inputAnnualReports: ['腾讯控股有限公司_2024.pdf', '腾讯控股有限公司_2023.pdf'],
    sampleOutputReport: 'sample004.md',
  },
  {
    market: 'SG',
    companyName: 'Food Empire Holdings Ltd',
    inputAnnualReports: [
      'Food Empire Holdings Limited_2024.pdf',
      'Food Empire Holdings Limited_2023.pdf',
    ],
    sampleOutputReport: 'sample005.md',
  },
  {
    market: 'AU',
    companyName: 'CSL Ltd',
    inputAnnualReports: ['CSL Limited_2024.pdf', 'CSL Limited_2023.pdf'],
    sampleOutputReport: 'sample006.md',
  },
  {
    market: 'MY',
    companyName: 'IJM Corporation Berhad',
    inputAnnualReports: ['IJM Corporation Berhad_2024.pdf', 'IJM Corporation Berhad_2023.pdf'],
    sampleOutputReport: 'sample007.md',
  },
  {
    market: 'ID',
    companyName: 'PT Garudafood Putra Putri Jaya Tbk',
    inputAnnualReports: [
      'PT Garudafood Putra Putri Jaya Tbk_2024.pdf',
      'PT Garudafood Putra Putri Jaya Tbk_2023.pdf',
    ],
    sampleOutputReport: 'sample008.md',
  },
]

export const dataset: Dataset[] = [
  {
    market: 'US',
    companyCount: 10,
    documentCount: 20,
    maxPageCount: 444,
    minPageCount: 82,
    avgPageCount: 178,
    examples: ['Williams-Sonoma Inc', 'UnitedHealth Group Incorporated'],
  },
  {
    market: 'UK',
    companyCount: 10,
    documentCount: 20,
    maxPageCount: 481,
    minPageCount: 105,
    avgPageCount: 235,
    examples: ['Shell PLC', 'Unilever PLC'],
  },
  {
    market: 'CN',
    companyCount: 10,
    documentCount: 20,
    maxPageCount: 353,
    minPageCount: 143,
    avgPageCount: 225,
    examples: ['上汽集团股份有限公司', '中国电信股份有限公司'],
  },
  {
    market: 'HK',
    companyCount: 10,
    documentCount: 20,
    maxPageCount: 353,
    minPageCount: 127,
    avgPageCount: 236,
    examples: ['美团', '中国海洋石油'],
  },
  {
    market: 'SG',
    companyCount: 10,
    documentCount: 20,
    maxPageCount: 268,
    minPageCount: 136,
    avgPageCount: 216,
    examples: ['IHH Healthcare Berhad', 'Raffles Medical Group Ltd'],
  },
  {
    market: 'AU',
    companyCount: 10,
    documentCount: 20,
    maxPageCount: 254,
    minPageCount: 79,
    avgPageCount: 139,
    examples: ['BHP Group Ltd', 'Metcash Ltd'],
  },
  {
    market: 'MY',
    companyCount: 10,
    documentCount: 20,
    maxPageCount: 280,
    minPageCount: 132,
    avgPageCount: 200,
    examples: ['Far East Holdings Berhad', 'UOA Development Berhad'],
  },
  {
    market: 'ID',
    companyCount: 10,
    documentCount: 20,
    maxPageCount: 599,
    minPageCount: 204,
    avgPageCount: 383,
    examples: ['PT Harum Energy Tbk', 'PT Bumi Serpong Damai Tbk'],
  },
]

export const scoreData: ScoreItem[] = [
  {
    method: 'FinFiler Agent',
    organization: 'Rensselaer Polytechnic Institute',
    score: 68.8,
    team: 'Finsselear',
    submittedDate: '2025/10/23',
    us: 67.0,
    uk: 68.3,
    cn: 68.6,
    hk: 69.7,
    sg: 71.4,
    au: 66.6,
    ind: 64.4,
    my: 74.5,
    model: 'rpi'
  },
  {
    method: 'PIKE-Report',
    organization: 'Microsoft Research Asia',
    score: 67.7,
    team: 'Token Refund',
    submittedDate: '2025/10/23',
    us: 64.2,
    uk: 67.9,
    cn: 64.9,
    hk: 67.8,
    sg: 68.8,
    au: 70.2,
    ind: 66.9,
    my: 71.1,
    model: 'microsoft'
  },
  {
    method: 'Deepseek-v3.2',
    organization: 'Official',
    score: 62.7,
    team: 'Baseline',
    submittedDate: '2025/10/15',
    us: 68.3,
    uk: 60.4,
    cn: 58.6,
    hk: 59.9,
    sg: 66.0,
    au: 58.3,
    ind: 61.4,
    my: 68.6,
    model: 'deepseek'
  },
  {
    method: 'GPT-5-MINI with File Search',
    organization: 'Official',
    score: 61.8,
    team: 'Baseline',
    submittedDate: '2025/10/15',
    us: 64.5,
    uk: 61.8,
    cn: 54.9,
    hk: 59.5,
    sg: 65.4,
    au: 64.4,
    ind: 57.9,
    my: 65.7,
    model: 'chatgpt'
  },
  {
    method: 'SilverSight Agent',
    organization: 'Fudan University, Shanghai Innovation Institute, DataGrand Inc',
    score: 59.5,
    team: 'SilverSight',
    submittedDate: '2025/10/23',
    us: 57.4,
    uk: 57.7,
    cn: 59.9,
    hk: 60.3,
    sg: 60.9,
    au: 60.0,
    ind: 55.8,
    my: 63.9
  },
  {
    method: 'GPT-5-NANO',
    organization: 'Official',
    score: 58.2,
    team: 'Baseline',
    submittedDate: '2025/10/15',
    us: 61.4,
    uk: 59.1,
    cn: 51.2,
    hk: 50.0,
    sg: 67.5,
    au: 58.1,
    ind: 54.5,
    my: 63.6,
    model: 'chatgpt'
  },
  {
    method: 'afinit_fin_report_agent_v2',
    organization: 'afinit',
    score: 53.4,
    team: 'afinit',
    submittedDate: '2025/10/23',
    us: 58.1,
    uk: 51.7,
    cn: 62.3,
    hk: 46.3,
    sg: 54.2,
    au: 53.2,
    ind: 45.1,
    my: 56.0,
    model: 'default'
  },
  {
    method: 'ICTDR',
    organization: 'Chinese Academy of Sciences',
    score: 51.2,
    team: 'ICT-NDST',
    submittedDate: '2025/10/22',
    us: 55.6,
    uk: 53.4,
    cn: 40.9,
    hk: 51.2,
    sg: 55.2,
    au: 49.0,
    ind: 48.8,
    my: 55.2,
    model: 'cas',
    imageType: 'jpg'
  },
  {
    method: 'GPT-OSS-20B',
    organization: 'Official',
    score: 46.1,
    team: 'Baseline',
    submittedDate: '2025/10/15',
    us: 49.3,
    uk: 37.5,
    cn: 37.2,
    hk: 43.7,
    sg: 50.5,
    au: 45.8,
    ind: 49.5,
    my: 55.4,
    model: 'chatgpt'
  },
  {
    method: 'GeminiFlashRAG',
    organization: 'A*STAR',
    score: 35.5,
    team: 'SI4Fin',
    submittedDate: '2025/10/21',
    us: 40.4,
    uk: 33.6,
    cn: 33.3,
    hk: 39.2,
    sg: 42.7,
    au: 32.8,
    ind: 26.6,
    my: 35.1,
    model: 'astar',
    imageType: 'png'
  },
  {
    method: 'DeepFin Agent',
    organization: 'Renmin University of China',
    score: 18.3,
    team: 'RUCFnAI',
    submittedDate: '2025/10/22',
    us: 19.8,
    uk: 14.7,
    cn: 14.5,
    hk: 20.3,
    sg: 26.2,
    au: 16.7,
    ind: 15.6,
    my: 18.2,
    model: 'ruc',
    imageType: 'png'
  }
]
