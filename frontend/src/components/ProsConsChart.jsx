import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts';

const ProsConsChart = ({ keywordsData }) => {
  // Check if data exists
  if (!keywordsData || (!keywordsData.positive.length && !keywordsData.negative.length)) {
    return <div style={{textAlign: 'center', padding: '20px', color: '#666'}}>No enough data for this group.</div>;
  }

  // Transform data: Positives get positive score, Negatives get negative score
  const data = [
    ...keywordsData.positive.map((k, i) => ({ name: k, score: 5 - i, type: 'positive' })),
    ...keywordsData.negative.map((k, i) => ({ name: k, score: -(5 - i), type: 'negative' }))
  ];

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        layout="vertical"
        data={data}
        margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
        stackOffset="sign"
      >
        {/* Hidden X Axis keeps the bars centered properly */}
        <XAxis type="number" hide domain={[-6, 6]} />
        
        {/* Y Axis displays the keywords */}
        <YAxis 
          dataKey="name" 
          type="category" 
          tick={{ fontSize: 12, width: 100 }} 
          width={100}
          interval={0}
        />
        
        <Tooltip 
          cursor={{fill: 'transparent'}}
          content={({ payload }) => {
            if (payload && payload.length) {
              const item = payload[0].payload;
              return (
                <div style={{ backgroundColor: '#fff', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}>
                  <p style={{ color: item.type === 'positive' ? '#4caf50' : '#e53935', fontWeight: 'bold', margin: 0 }}>
                    {item.type.toUpperCase()}: {item.name}
                  </p>
                </div>
              );
            }
            return null;
          }}
        />
        
        <ReferenceLine x={0} stroke="#ccc" />
        
        <Bar dataKey="score" barSize={20} radius={[4, 4, 4, 4]}>
          {data.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={entry.type === 'positive' ? '#4caf50' : '#e53935'} 
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export default ProsConsChart;