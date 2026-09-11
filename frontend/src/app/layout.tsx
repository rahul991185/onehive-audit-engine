import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'OneHive Digital Presence Intelligence | Sales Engine',
  description: 'Enterprise internal sales tool analyzing business digital presence and generating verified 5-page OneHive PDF consulting reports.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/onehive_logo.png" />
      </head>
      <body>
        <div className="ambient-glow-top"></div>
        <div className="ambient-glow-bottom"></div>
        {children}
      </body>
    </html>
  );
}
