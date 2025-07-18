import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider" // Assuming you have this from shadcn/ui setup
import { AuthProvider } from "@/contexts/auth-context"
import { AuthErrorBoundary } from "@/components/auth/auth-error-boundary"
import { Toaster } from "@/components/ui/toaster" // For toast notifications

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })

export const metadata: Metadata = {
  title: "Dynamic English Course Creator",
  description: "AI-Powered English Language Learning Platform",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <AuthErrorBoundary>
            <AuthProvider>
              {children}
              <Toaster />
            </AuthProvider>
          </AuthErrorBoundary>
        </ThemeProvider>
      </body>
    </html>
  )
}
