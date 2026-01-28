// SentimentBarChart.jsx
import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
} from "recharts";

const sampleSentimentData = [
  { user: "Gamers", positive: 42, neutral: 5, negative: 4 },
  { user: "Students", positive: 35, neutral: 1, negative: 6 },
  { user: "Content Creators", positive: 26, neutral: 3, negative: 1 },
  { user: "Casual Users", positive: 34, neutral: 2, negative: 4 },
  { user: "Programmers", positive: 34, neutral: 2, negative: 5 },
];

const SentimentChart = ({data}) => (
  <ResponsiveContainer width="100%" height={300}>
    <BarChart data={data} margin={{ top: 20, right: 30, bottom: 20, left: 0 }}>
      <XAxis dataKey="user" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Bar dataKey="positive" fill="#4caf50" />
      <Bar dataKey="neutral" fill="#ffb300" />
      <Bar dataKey="negative" fill="#e53935" />
    </BarChart>
  </ResponsiveContainer>
);

export default SentimentChart;




// 
// ProsConsChart.jsx
// import React from 'react';
// import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts';

// const ProsConsChart = ({ keywordsData }) => {
//   // keywordsData expects: { positive: ["..."], negative: ["..."] }
//   if (!keywordsData) return null;

//   // Transform data for the chart
//   // We give negatives a negative score value so they plot to the left
//   const data = [
//     ...keywordsData.positive.map((k, i) => ({ name: k, score: 5 - i, type: 'positive' })),
//     ...keywordsData.negative.map((k, i) => ({ name: k, score: -(5 - i), type: 'negative' }))
//   ];

//   return (
//     <div className="w-full p-4 border rounded shadow-sm bg-white">
//       <h3 className="text-center font-bold mb-4">Top Pros & Cons</h3>
//       <ResponsiveContainer width="100%" height={350}>
//         <BarChart
//           layout="vertical"
//           data={data}
//           margin={{ top: 5, right: 30, left: 30, bottom: 5 }}
//           stackOffset="sign"
//         >
//           {/* Hidden X Axis just to set the range */}
//           <XAxis type="number" hide domain={[-6, 6]} />
          
//           {/* Y Axis displays the keywords */}
//           <YAxis 
//             dataKey="name" 
//             type="category" 
//             tick={{ fontSize: 12, width: 150 }} 
//             width={120}
//             interval={0}
//           />
          
//           <Tooltip 
//             cursor={{fill: 'transparent'}}
//             content={({ payload }) => {
//               if (payload && payload.length) {
//                 const data = payload[0].payload;
//                 return (
//                   <div className="bg-white p-2 border shadow-lg rounded">
//                     <p style={{ color: data.type === 'positive' ? '#4caf50' : '#e53935', fontWeight: 'bold' }}>
//                       {data.type.toUpperCase()}: {data.name}
//                     </p>
//                   </div>
//                 );
//               }
//               return null;
//             }}
//           />
          
//           <ReferenceLine x={0} stroke="#ccc" />
          
//           <Bar dataKey="score" barSize={20} radius={[4, 4, 4, 4]}>
//             {data.map((entry, index) => (
//               <Cell 
//                 key={`cell-${index}`} 
//                 fill={entry.type === 'positive' ? '#4caf50' : '#e53935'} 
//               />
//             ))}
//           </Bar>
//         </BarChart>
//       </ResponsiveContainer>
//     </div>
//   );
// };

// export default ProsConsChart;