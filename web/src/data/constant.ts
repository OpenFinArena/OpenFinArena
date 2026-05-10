export interface OptionItem {
  label: string
  value: string
  src?: string
}

export const DOC_DEEP_COUNTRY_TAB: OptionItem[] = [
  { label: 'Overall', value: 'overall', src: '/images/flag/medal.svg' },
  { label: 'US', value: 'us', src: '/images/flag/us.svg' },
  { label: 'UK', value: 'uk', src: '/images/flag/uk.svg' },
  { label: 'CN', value: 'cn', src: '/images/flag/cn.svg' },
  { label: 'HK', value: 'hk', src: '/images/flag/hk.svg' },
  { label: 'SG', value: 'sg', src: '/images/flag/sg.svg' },
  { label: 'AU', value: 'au', src: '/images/flag/au.svg' },
  { label: 'MY', value: 'my', src: '/images/flag/my.svg' },
  { label: 'ID', value: 'ind', src: '/images/flag/id.svg' },
]

export const FORECAST_TABS: OptionItem[] = [
  { label: 'Corporate Financial Forecasting', value: 'corporate' },
  { label: 'Macroeconomic Indicator Forecasting', value: 'macroeconomic' }
]

export const PERIOD_TABS: OptionItem[] = [
  { label: 'Overall', value: 'overall', src: '/images/flag/medal.svg' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
  // { label: 'Quarterly', value: 'quarterly' },
  // { label: 'Yearly', value: 'yearly' }
]

export const QUARTER_OPTIONS: OptionItem[] = [
  { value: 'Q1', label: 'Q1' },
  { value: 'Q2', label: 'Q2' },
  { value: 'Q3', label: 'Q3' },
  { value: 'Q4', label: 'Q4' }
]

export const FORECAST_COUNTRY_TABS: OptionItem[] = [
  { label: 'US', value: 'us', src: '/images/flag/us.svg' },
  { label: 'CN', value: 'cn', src: '/images/flag/cn.svg' },
  { label: 'HK', value: 'hk', src: '/images/flag/hk.svg' },
  { label: 'JP', value: 'jp', src: '/images/flag/jp.svg' },
  { label: 'UK', value: 'uk', src: '/images/flag/uk.svg' },
  { label: 'DE', value: 'de', src: '/images/flag/de.svg' },
  { label: 'FR', value: 'fr', src: '/images/flag/fr.svg' },
  { label: 'SG', value: 'sg', src: '/images/flag/sg.svg' },
]

export const GLOBAL_INDEX_TABS: OptionItem[] = [
  { label: 'NASDAQ 100', value: 'nasdaq 100', src: '/images/flag/us.svg' },
  { label: 'S&P 500', value: 's&p 500', src: '/images/flag/us.svg' },
  { label: 'CSI 300', value: 'csi 300', src: '/images/flag/cn.svg' },
  { label: 'Nikkei 225', value: 'nikkei 225', src: '/images/flag/jp.svg' },
  { label: 'FTSE 100', value: 'ftse 100', src: '/images/flag/uk.svg' },
  { label: 'DAX 40', value: 'dax 40', src: '/images/flag/de.svg' },
  { label: 'CAC 40', value: 'cac 40', src: '/images/flag/fr.svg' },
  { label: 'HSI', value: 'hsi', src: '/images/flag/hk.svg' },
  { label: 'STI', value: 'sti', src: '/images/flag/sg.svg' },
]

const MARKET_TABS: OptionItem[] = [
  { label: 'Overall', value: 'overall', src: '/images/flag/medal.svg' },
  { label: 'Nasdaq-100 Index', value: 'us' },
  { label: 'Nikkei 225 Index', value: 'jp' },
  { label: 'CSI 300 Index', value: 'cn' },
  { label: 'Hang Seng Index', value: 'hk' },
  { label: 'SGX Straits Times Index', value: 'sg' }
]

export const TYPE_TABS: OptionItem[] = [
  { label: 'Recurrent', value: 'Recurrent' },
  { label: 'Situational', value: 'Situational' }
]