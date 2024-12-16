import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Guardrails - Safety Framework for AI Agents',
  description: 'A powerful validation and safety framework that ensures AI agents operate within defined boundaries and ethical guidelines.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
} 