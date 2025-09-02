import React from 'react';

interface DataPoint {
  date: string;
  value: number;
}

interface PerformanceChartProps {
  data: DataPoint[];
  title?: string;
  color?: 'success' | 'danger' | 'primary';
}

export function PerformanceChart({
  data,
  title = 'Performance Chart',
  color = 'primary',
}: PerformanceChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className='card-elevated'>
        <h3 className='text-xl font-bold text-retro-brown-700 mb-4'>{title}</h3>
        <div className='flex items-center justify-center h-64 neumorph-inset rounded-2xl'>
          <p className='text-retro-brown-500'>No data available</p>
        </div>
      </div>
    );
  }

  const width = 800;
  const height = 300;
  const padding = 40;

  const maxValue = Math.max(...data.map(d => d.value));
  const minValue = Math.min(...data.map(d => d.value));
  const valueRange = maxValue - minValue || 1;

  const colorMap = {
    success: '#68C7C1', // retro-turquoise
    danger: '#DD3341', // retro-red
    primary: '#68C7C1', // retro-turquoise
  };

  const strokeColor = colorMap[color];
  const fillColor = strokeColor + '20'; // Add transparency

  // Create path data
  const pathData = data
    .map((point, index) => {
      const x = padding + (index / (data.length - 1)) * (width - 2 * padding);
      const y =
        padding +
        ((maxValue - point.value) / valueRange) * (height - 2 * padding);
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
    })
    .join(' ');

  // Create area path (for fill)
  const areaPath =
    pathData +
    ` L ${padding + (width - 2 * padding)} ${height - padding}` +
    ` L ${padding} ${height - padding} Z`;

  return (
    <div className='card-elevated'>
      <div className='flex justify-between items-center mb-6'>
        <h3 className='text-xl font-bold text-retro-brown-700'>{title}</h3>
        <div className='flex items-center space-x-4'>
          <div className='flex items-center space-x-2'>
            <div
              className={`w-3 h-3 rounded-full ${
                color === 'danger'
                  ? 'bg-retro-red-500'
                  : 'bg-retro-turquoise-500'
              }`}
            ></div>
            <span className='text-sm text-retro-brown-600'>Profit/Loss</span>
          </div>
        </div>
      </div>

      <div className='relative'>
        <svg
          width='100%'
          height={height}
          viewBox={`0 0 ${width} ${height}`}
          className='overflow-visible'
        >
          {/* Grid lines */}
          <defs>
            <pattern
              id='grid'
              width='40'
              height='40'
              patternUnits='userSpaceOnUse'
            >
              <path
                d='M 40 0 L 0 0 0 40'
                fill='none'
                stroke='#e5e7eb'
                strokeWidth='1'
                opacity='0.3'
              />
            </pattern>
          </defs>
          <rect width='100%' height='100%' fill='url(#grid)' />

          {/* Area fill */}
          <path
            d={areaPath}
            fill={fillColor}
            className='transition-all duration-300'
          />

          {/* Main line */}
          <path
            d={pathData}
            fill='none'
            stroke={strokeColor}
            strokeWidth='3'
            strokeLinecap='round'
            strokeLinejoin='round'
            className='transition-all duration-300'
          />

          {/* Data points */}
          {data.map((point, index) => {
            const x =
              padding + (index / (data.length - 1)) * (width - 2 * padding);
            const y =
              padding +
              ((maxValue - point.value) / valueRange) * (height - 2 * padding);

            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r='4'
                fill={strokeColor}
                className='transition-all duration-300 hover:r-6 cursor-pointer'
              >
                <title>{`${point.date}: $${point.value.toFixed(2)}`}</title>
              </circle>
            );
          })}

          {/* Y-axis labels */}
          {[0, 0.25, 0.5, 0.75, 1].map(ratio => {
            const value = minValue + ratio * valueRange;
            const y = padding + (1 - ratio) * (height - 2 * padding);

            return (
              <g key={ratio}>
                <line
                  x1={padding - 5}
                  y1={y}
                  x2={padding}
                  y2={y}
                  stroke='#6b7280'
                  strokeWidth='1'
                />
                <text
                  x={padding - 10}
                  y={y + 4}
                  textAnchor='end'
                  className='text-xs fill-gray-500'
                >
                  ${value.toFixed(0)}
                </text>
              </g>
            );
          })}

          {/* X-axis labels */}
          {data.map((point, index) => {
            if (index % Math.ceil(data.length / 6) === 0) {
              const x =
                padding + (index / (data.length - 1)) * (width - 2 * padding);

              return (
                <g key={index}>
                  <line
                    x1={x}
                    y1={height - padding}
                    x2={x}
                    y2={height - padding + 5}
                    stroke='#6b7280'
                    strokeWidth='1'
                  />
                  <text
                    x={x}
                    y={height - padding + 20}
                    textAnchor='middle'
                    className='text-xs fill-gray-500'
                  >
                    {new Date(point.date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </text>
                </g>
              );
            }
            return null;
          })}
        </svg>
      </div>

      <div className='mt-6 grid grid-cols-3 gap-4'>
        <div className='neumorph-inset p-4 text-center rounded-2xl'>
          <p className='text-xs text-retro-brown-500 uppercase tracking-wide mb-1'>
            Highest
          </p>
          <p className='font-bold text-retro-brown-700'>
            ${maxValue.toFixed(2)}
          </p>
        </div>
        <div className='neumorph-inset p-4 text-center rounded-2xl'>
          <p className='text-xs text-retro-brown-500 uppercase tracking-wide mb-1'>
            Average
          </p>
          <p className='font-bold text-retro-brown-700'>
            $
            {(
              data.reduce((sum, point) => sum + point.value, 0) / data.length
            ).toFixed(2)}
          </p>
        </div>
        <div className='neumorph-inset p-4 text-center rounded-2xl'>
          <p className='text-xs text-retro-brown-500 uppercase tracking-wide mb-1'>
            Lowest
          </p>
          <p className='font-bold text-retro-brown-700'>
            ${minValue.toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  );
}
