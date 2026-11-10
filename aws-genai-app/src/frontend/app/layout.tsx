import React from 'react';

export const metadata = {
  title: 'AWS GenAI Production App',
  description: 'Enterprise Generative AI architecture on AWS',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, backgroundColor: '#f1f5f9' }}>
        {children}
      </body>
    </html>
  );
}
