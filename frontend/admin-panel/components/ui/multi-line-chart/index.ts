export interface BaseMultiLineChartProps<T> {
	data: T[]

	height?: number

	showLegend?: boolean

	numTicks?: number

	colors?: string[]

	x: (d: T) => number | Date

	yLabel?: string

	xTickFormat?: (value: any) => string

	series: {
		key: keyof T
		label?: string
		y: (d: T) => number
	}[]
}